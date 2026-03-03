import { validate } from "../middleware/validate.js";
import { createJWT, generateSalt, generateUUID, hashPassword, timingSafeEqual } from "../utils/crypto.js";
import { errorResponse, successResponse } from "../utils/http.js";

const USERNAME_PATTERN = /^[a-zA-Z0-9]+$/;

const registerSchema = {
  username: { type: "string", required: true, min: 3, max: 30, pattern: USERNAME_PATTERN },
  password: { type: "string", required: true, min: 8 },
};

const loginSchema = {
  username: { type: "string", required: true, min: 3, max: 30 },
  password: { type: "string", required: true, min: 8 },
};

async function findUserByUsername(db, username) {
  const users = await db.getAll("users", {
    index: "username",
    range: IDBKeyRange.only(username),
  });
  return users[0] ?? null;
}

function sanitizeUser(user) {
  return {
    id: user.id,
    username: user.username,
    created_at: user.created_at,
    last_login: user.last_login,
  };
}

export function registerAuthRoutes(router, { db, jwtSecret, authRateLimit }) {
  router.post(
    "/api/auth/register",
    authRateLimit("auth:register"),
    validate(registerSchema, { allowUnknown: false }),
    async (req) => {
      const username = req.body.username.trim().toLowerCase();
      const password = req.body.password;

      const existingUser = await findUserByUsername(db, username);
      if (existingUser) {
        return errorResponse(409, "Username is already registered");
      }

      const now = Date.now();
      const salt = generateSalt();
      const pwHash = await hashPassword(password, salt);
      const user = {
        id: generateUUID(),
        username,
        pw_hash: pwHash,
        pw_salt: salt,
        created_at: now,
        last_login: null,
      };

      const auditEntry = {
        id: generateUUID(),
        user_id: user.id,
        action: "auth.register",
        resource_id: user.id,
        detail: JSON.stringify({ username: user.username }),
        timestamp: now,
      };

      await db.transaction(["users", "audit_log"], "readwrite", (stores) => {
        stores.users.put(user);
        stores.audit_log.put(auditEntry);
      });

      const token = await createJWT({ sub: user.id, username: user.username }, jwtSecret);
      return successResponse(
        {
          token,
          user: sanitizeUser(user),
        },
        { status: 201 },
      );
    },
  );

  router.post(
    "/api/auth/login",
    authRateLimit("auth:login"),
    validate(loginSchema, { allowUnknown: false }),
    async (req) => {
      const username = req.body.username.trim().toLowerCase();
      const password = req.body.password;

      const user = await findUserByUsername(db, username);
      if (!user) {
        return errorResponse(401, "Invalid username or password");
      }

      const providedHash = await hashPassword(password, user.pw_salt);
      const isValid = timingSafeEqual(providedHash, user.pw_hash);
      if (!isValid) {
        return errorResponse(401, "Invalid username or password");
      }

      const now = Date.now();
      const updatedUser = {
        ...user,
        last_login: now,
      };

      const auditEntry = {
        id: generateUUID(),
        user_id: user.id,
        action: "auth.login",
        resource_id: user.id,
        detail: JSON.stringify({ username: user.username }),
        timestamp: now,
      };

      await db.transaction(["users", "audit_log"], "readwrite", (stores) => {
        stores.users.put(updatedUser);
        stores.audit_log.put(auditEntry);
      });

      const token = await createJWT({ sub: user.id, username: user.username }, jwtSecret);
      return successResponse({
        token,
        user: sanitizeUser(updatedUser),
      });
    },
  );
}

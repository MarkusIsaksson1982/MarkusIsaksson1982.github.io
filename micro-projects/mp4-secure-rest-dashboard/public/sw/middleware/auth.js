import { verifyJWT } from "../utils/crypto.js";
import { errorResponse } from "../utils/http.js";

function parseBearerToken(authorizationHeader) {
  if (!authorizationHeader || typeof authorizationHeader !== "string") {
    return null;
  }
  const [scheme, token] = authorizationHeader.trim().split(/\s+/, 2);
  if (!scheme || !token || scheme.toLowerCase() !== "bearer") {
    return null;
  }
  return token;
}

export function createAuthMiddleware({ secret }) {
  if (!secret) {
    throw new Error("Auth middleware requires a JWT secret");
  }

  return async (req, next) => {
    const authorization = req.headers.get("authorization");
    const token = parseBearerToken(authorization);
    if (!token) {
      return errorResponse(401, "Missing or invalid authorization header");
    }

    const payload = await verifyJWT(token, secret);
    if (!payload) {
      return errorResponse(401, "Invalid or expired token");
    }

    const userId = payload.sub ?? payload.id;
    if (!userId || !payload.username) {
      return errorResponse(401, "Invalid token payload");
    }

    req.user = {
      id: userId,
      username: payload.username,
    };

    return next();
  };
}

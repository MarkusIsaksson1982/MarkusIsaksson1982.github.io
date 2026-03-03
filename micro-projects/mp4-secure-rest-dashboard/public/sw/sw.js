import { Router } from "./router.js";
import { createDatabaseConnection } from "./db/connection.js";
import { seedDatabase } from "./db/seed.js";
import { createAuthMiddleware } from "./middleware/auth.js";
import { createRateLimiter } from "./middleware/rateLimit.js";
import { registerAuthRoutes } from "./routes/auth.js";
import { registerTaskRoutes } from "./routes/tasks.js";
import { registerAnalyticsRoutes } from "./routes/analytics.js";
import { errorResponse } from "./utils/http.js";

const JWT_SECRET = "mp4-demo-service-worker-jwt-secret";

const db = createDatabaseConnection();
const router = new Router();
const requireAuth = createAuthMiddleware({ secret: JWT_SECRET });
const authRateLimit = createRateLimiter({
  maxTokens: 5,
  refillRate: 5,
  refillInterval: 60_000,
});
const apiRateLimit = createRateLimiter({
  maxTokens: 60,
  refillRate: 60,
  refillInterval: 60_000,
});

registerAuthRoutes(router, { db, jwtSecret: JWT_SECRET, authRateLimit });
registerTaskRoutes(router, { db, requireAuth, apiRateLimit });
registerAnalyticsRoutes(router, { db, requireAuth, apiRateLimit });

let initPromise = null;

async function initializeBackend() {
  if (!initPromise) {
    initPromise = (async () => {
      await db.open();
      await seedDatabase(db);
    })().catch((error) => {
      initPromise = null;
      throw error;
    });
  }
  return initPromise;
}

function isApiRequest(request) {
  const url = new URL(request.url);
  return url.origin === self.location.origin && url.pathname.startsWith("/api/");
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      await initializeBackend();
      await self.skipWaiting();
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (event) => {
  if (!isApiRequest(event.request)) {
    return;
  }

  event.respondWith(
    (async () => {
      try {
        await initializeBackend();
        return await router.handle(event.request, { db });
      } catch {
        return errorResponse(500, "Failed to initialize service worker backend");
      }
    })(),
  );
});

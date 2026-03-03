import { jsonResponse } from "../utils/http.js";

function nowMs() {
  return Date.now();
}

export function createRateLimiter({
  maxTokens = 60,
  refillRate = 60,
  refillInterval = 60_000,
} = {}) {
  if (maxTokens <= 0 || refillRate <= 0 || refillInterval <= 0) {
    throw new Error("Rate limiter config must use positive values");
  }

  const buckets = new Map();

  function refillBucket(bucket, timestamp) {
    const elapsed = timestamp - bucket.lastRefill;
    if (elapsed <= 0) {
      return bucket;
    }
    const refillAmount = (elapsed / refillInterval) * refillRate;
    return {
      tokens: Math.min(maxTokens, bucket.tokens + refillAmount),
      lastRefill: timestamp,
    };
  }

  return function rateLimit(routeKey = "global") {
    return async (req, next) => {
      const identity =
        req.user?.id ??
        req.headers.get("x-client-id") ??
        req.headers.get("authorization") ??
        "anonymous";
      const key = `${routeKey}:${identity}`;
      const timestamp = nowMs();
      const current = buckets.get(key) ?? { tokens: maxTokens, lastRefill: timestamp };
      const bucket = refillBucket(current, timestamp);

      if (bucket.tokens < 1) {
        const missingTokens = 1 - bucket.tokens;
        const retryMs = (missingTokens / refillRate) * refillInterval;
        const retryAfterSeconds = Math.max(1, Math.ceil(retryMs / 1000));
        buckets.set(key, bucket);
        return jsonResponse(
          {
            error: true,
            status: 429,
            message: "Rate limit exceeded",
          },
          {
            status: 429,
            headers: { "Retry-After": String(retryAfterSeconds) },
          },
        );
      }

      bucket.tokens -= 1;
      buckets.set(key, bucket);
      return next();
    };
  };
}

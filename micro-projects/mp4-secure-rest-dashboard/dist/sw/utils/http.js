const JSON_HEADERS = {
  "Content-Type": "application/json; charset=utf-8",
  "Cache-Control": "no-store",
};

export function jsonResponse(body, { status = 200, headers = {} } = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      ...JSON_HEADERS,
      ...headers,
    },
  });
}

export function successResponse(data, { status = 200, meta } = {}) {
  const payload = meta ? { data, meta } : { data };
  return jsonResponse(payload, { status });
}

export function errorResponse(status, message, details) {
  const payload = {
    error: true,
    status,
    message,
  };

  if (details) {
    payload.details = details;
  }

  return jsonResponse(payload, { status });
}

export function safeNumber(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

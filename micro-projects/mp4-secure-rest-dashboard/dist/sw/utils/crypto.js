const encoder = new TextEncoder();
const DEFAULT_JWT_TTL_SECONDS = 15 * 60;

function toBase64Url(bytes) {
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function fromBase64Url(input) {
  const base64 = input.replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64 + "=".repeat((4 - (base64.length % 4 || 4)) % 4);
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

function normalizeSecret(secret) {
  if (secret instanceof Uint8Array) {
    return secret;
  }
  return encoder.encode(String(secret));
}

async function importPBKDF2Key(password) {
  return crypto.subtle.importKey("raw", encoder.encode(password), "PBKDF2", false, ["deriveBits"]);
}

async function importHMACKey(secret, usage) {
  return crypto.subtle.importKey(
    "raw",
    normalizeSecret(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    [usage],
  );
}

export function generateSalt() {
  const salt = new Uint8Array(16);
  crypto.getRandomValues(salt);
  return toBase64Url(salt);
}

export async function hashPassword(password, salt) {
  const saltBytes = typeof salt === "string" ? fromBase64Url(salt) : salt;
  const passwordKey = await importPBKDF2Key(password);
  const bits = await crypto.subtle.deriveBits(
    {
      name: "PBKDF2",
      hash: "SHA-256",
      salt: saltBytes,
      iterations: 100_000,
    },
    passwordKey,
    256,
  );
  return toBase64Url(new Uint8Array(bits));
}

function encodeSegment(payload) {
  return toBase64Url(encoder.encode(JSON.stringify(payload)));
}

function decodeSegment(segment) {
  const bytes = fromBase64Url(segment);
  return JSON.parse(new TextDecoder().decode(bytes));
}

export async function createJWT(payload, secret) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: "HS256", typ: "JWT" };
  const claims = {
    iat: payload?.iat ?? now,
    exp: payload?.exp ?? now + DEFAULT_JWT_TTL_SECONDS,
    ...payload,
  };

  const headerSegment = encodeSegment(header);
  const payloadSegment = encodeSegment(claims);
  const signingInput = `${headerSegment}.${payloadSegment}`;
  const key = await importHMACKey(secret, "sign");
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(signingInput));
  const signatureSegment = toBase64Url(new Uint8Array(signature));
  return `${signingInput}.${signatureSegment}`;
}

export async function verifyJWT(token, secret) {
  if (!token || typeof token !== "string") {
    return null;
  }

  const parts = token.split(".");
  if (parts.length !== 3) {
    return null;
  }

  const [headerSegment, payloadSegment, signatureSegment] = parts;
  let header;
  let payload;
  try {
    header = decodeSegment(headerSegment);
    payload = decodeSegment(payloadSegment);
  } catch {
    return null;
  }

  if (header?.alg !== "HS256") {
    return null;
  }

  const signingInput = `${headerSegment}.${payloadSegment}`;
  const key = await importHMACKey(secret, "verify");
  const isValid = await crypto.subtle.verify(
    "HMAC",
    key,
    fromBase64Url(signatureSegment),
    encoder.encode(signingInput),
  );

  if (!isValid) {
    return null;
  }

  const now = Math.floor(Date.now() / 1000);
  if (typeof payload.exp !== "number" || payload.exp <= now) {
    return null;
  }

  return payload;
}

export function timingSafeEqual(a, b) {
  const left = String(a ?? "");
  const right = String(b ?? "");
  const maxLength = Math.max(left.length, right.length);
  let mismatch = left.length ^ right.length;

  for (let i = 0; i < maxLength; i += 1) {
    const leftCode = i < left.length ? left.charCodeAt(i) : 0;
    const rightCode = i < right.length ? right.charCodeAt(i) : 0;
    mismatch |= leftCode ^ rightCode;
  }

  return mismatch === 0;
}

export function generateUUID() {
  if (typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

export const __cryptoInternals = {
  fromBase64Url,
  toBase64Url,
};

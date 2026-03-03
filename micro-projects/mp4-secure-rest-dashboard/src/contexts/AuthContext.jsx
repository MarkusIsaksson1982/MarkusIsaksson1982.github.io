import { createContext, useCallback, useContext, useMemo, useState } from "react";

const SESSION_STORAGE_KEY = "mp4_auth_session";
const AuthContext = createContext(null);

function readSessionStorage() {
  try {
    const raw = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) {
      return { token: null, user: null };
    }
    const parsed = JSON.parse(raw);
    if (!parsed?.token || !parsed?.user) {
      return { token: null, user: null };
    }
    return { token: parsed.token, user: parsed.user };
  } catch {
    return { token: null, user: null };
  }
}

function persistSessionStorage(token, user) {
  if (!token || !user) {
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
    return;
  }
  sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({ token, user }));
}

function parseResponseError(response, payload) {
  const retryAfter = response.headers.get("Retry-After");
  return {
    status: response.status,
    message: payload?.message ?? `Request failed (${response.status})`,
    details: payload?.details ?? null,
    retryAfter: retryAfter ? Number(retryAfter) : null,
    payload,
  };
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(readSessionStorage);

  const setAuthenticatedSession = useCallback((token, user) => {
    const next = { token, user };
    setSession(next);
    persistSessionStorage(token, user);
  }, []);

  const logout = useCallback(() => {
    setSession({ token: null, user: null });
    persistSessionStorage(null, null);
  }, []);

  const apiFetch = useCallback(
    async (url, options = {}) => {
      const { body, headers, skipAuth = false, ...fetchOptions } = options;
      const requestHeaders = new Headers(headers ?? {});

      if (!skipAuth && session.token && !requestHeaders.has("Authorization")) {
        requestHeaders.set("Authorization", `Bearer ${session.token}`);
      }

      let requestBody = body;
      const isBodyObject =
        body !== null &&
        body !== undefined &&
        typeof body === "object" &&
        !(body instanceof FormData) &&
        !(body instanceof Blob) &&
        !(body instanceof URLSearchParams);

      if (isBodyObject) {
        requestBody = JSON.stringify(body);
        if (!requestHeaders.has("Content-Type")) {
          requestHeaders.set("Content-Type", "application/json");
        }
      }

      const response = await fetch(url, {
        ...fetchOptions,
        headers: requestHeaders,
        body: requestBody,
      });

      const raw = await response.text();
      let payload = null;
      if (raw) {
        try {
          payload = JSON.parse(raw);
        } catch {
          payload = { message: raw };
        }
      }

      if (!response.ok) {
        if (response.status === 401 && !skipAuth && session.token) {
          logout();
        }
        throw parseResponseError(response, payload);
      }

      return payload;
    },
    [logout, session.token],
  );

  const login = useCallback(
    async ({ username, password }) => {
      const response = await apiFetch("/api/auth/login", {
        method: "POST",
        body: { username, password },
        skipAuth: true,
      });
      const data = response?.data;
      setAuthenticatedSession(data?.token, data?.user);
      return data?.user ?? null;
    },
    [apiFetch, setAuthenticatedSession],
  );

  const register = useCallback(
    async ({ username, password }) => {
      const response = await apiFetch("/api/auth/register", {
        method: "POST",
        body: { username, password },
        skipAuth: true,
      });
      const data = response?.data;
      setAuthenticatedSession(data?.token, data?.user);
      return data?.user ?? null;
    },
    [apiFetch, setAuthenticatedSession],
  );

  const value = useMemo(
    () => ({
      user: session.user,
      token: session.token,
      isAuthenticated: Boolean(session.token && session.user),
      login,
      register,
      logout,
      apiFetch,
    }),
    [apiFetch, login, logout, register, session.token, session.user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

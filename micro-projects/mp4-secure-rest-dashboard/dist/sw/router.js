import { errorResponse, successResponse } from "./utils/http.js";

class RouterHttpError extends Error {
  constructor(status, message, details) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

function compilePath(pathPattern) {
  const paramNames = [];
  const normalized = pathPattern.replace(/\/+$/, "") || "/";
  const escaped = normalized
    .split("/")
    .map((segment) => {
      if (!segment) {
        return "";
      }
      if (segment.startsWith(":")) {
        const name = segment.slice(1).trim();
        if (!name) {
          throw new Error(`Invalid route param in path: ${pathPattern}`);
        }
        paramNames.push(name);
        return "([^/]+)";
      }
      return segment.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    })
    .join("/");

  const regex = new RegExp(`^${escaped || "/"}(?:/)?$`);
  return { regex, paramNames };
}

function extractParams(route, pathname) {
  const match = pathname.match(route.regex);
  if (!match) {
    return null;
  }
  const params = {};
  route.paramNames.forEach((name, index) => {
    params[name] = decodeURIComponent(match[index + 1] ?? "");
  });
  return params;
}

function parseQuery(searchParams) {
  const query = {};
  for (const [key] of searchParams.entries()) {
    const values = searchParams.getAll(key);
    query[key] = values.length > 1 ? values : values[0];
  }
  return query;
}

async function parseBody(request) {
  if (request.method === "GET" || request.method === "HEAD") {
    return null;
  }

  const contentType = request.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    const text = await request.text();
    return text ? { raw: text } : null;
  }

  const text = await request.text();
  if (!text) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new RouterHttpError(400, "Invalid JSON body");
  }
}

async function runMiddlewareStack(stack, req, index = 0) {
  if (index >= stack.length) {
    return undefined;
  }

  const current = stack[index];
  return current(req, () => runMiddlewareStack(stack, req, index + 1));
}

export class Router {
  constructor() {
    this.routes = [];
  }

  get(path, ...handlers) {
    this._register("GET", path, handlers);
    return this;
  }

  post(path, ...handlers) {
    this._register("POST", path, handlers);
    return this;
  }

  put(path, ...handlers) {
    this._register("PUT", path, handlers);
    return this;
  }

  delete(path, ...handlers) {
    this._register("DELETE", path, handlers);
    return this;
  }

  _register(method, path, handlers) {
    if (!path || typeof path !== "string") {
      throw new Error(`Invalid route path: ${path}`);
    }
    if (!Array.isArray(handlers) || handlers.length === 0) {
      throw new Error(`Route ${method} ${path} requires at least one handler`);
    }

    const flatHandlers = handlers.flat().filter(Boolean);
    if (flatHandlers.length === 0) {
      throw new Error(`Route ${method} ${path} has no executable handlers`);
    }

    const { regex, paramNames } = compilePath(path);
    const finalHandler = flatHandlers[flatHandlers.length - 1];
    const middlewares = flatHandlers.slice(0, -1);

    this.routes.push({
      method,
      path,
      regex,
      paramNames,
      middlewares,
      handler: finalHandler,
    });
  }

  async handle(request, context = {}) {
    const url = new URL(request.url);
    const pathname = url.pathname.replace(/\/+$/, "") || "/";
    const method = request.method.toUpperCase();

    const route = this.routes.find((candidate) => {
      if (candidate.method !== method) {
        return false;
      }
      return candidate.regex.test(pathname);
    });

    if (!route) {
      const hasPathMatch = this.routes.some((candidate) => candidate.regex.test(pathname));
      if (hasPathMatch) {
        return errorResponse(405, `Method ${method} not allowed`);
      }
      return errorResponse(404, "Route not found");
    }

    const params = extractParams(route, pathname) ?? {};
    const query = parseQuery(url.searchParams);

    try {
      const req = {
        request,
        method,
        url,
        path: pathname,
        params,
        query,
        headers: request.headers,
        body: await parseBody(request),
        user: null,
        context,
      };

      const stack = [...route.middlewares, route.handler];
      const result = await runMiddlewareStack(stack, req);

      if (result instanceof Response) {
        return result;
      }

      if (result === undefined) {
        return successResponse(null);
      }

      return successResponse(result);
    } catch (error) {
      if (error instanceof RouterHttpError) {
        return errorResponse(error.status, error.message, error.details);
      }
      return errorResponse(500, "Internal service worker backend error");
    }
  }
}

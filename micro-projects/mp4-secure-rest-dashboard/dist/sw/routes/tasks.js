import { validate } from "../middleware/validate.js";
import { generateUUID } from "../utils/crypto.js";
import { errorResponse, safeNumber, successResponse } from "../utils/http.js";

const STATUS_VALUES = ["todo", "in_progress", "done", "archived"];
const PRIORITY_VALUES = ["low", "medium", "high", "critical"];

const createTaskSchema = {
  title: { type: "string", required: true, min: 1, max: 140 },
  description: { type: "string", required: false, max: 4000 },
  status: { type: "string", required: false, enum: STATUS_VALUES },
  priority: { type: "string", required: false, enum: PRIORITY_VALUES },
  category: { type: "string", required: false, min: 2, max: 60 },
  due_date: { type: "number", required: false, min: 0 },
};

const updateTaskSchema = {
  title: { type: "string", required: false, min: 1, max: 140 },
  description: { type: "string", required: false, max: 4000 },
  status: { type: "string", required: false, enum: STATUS_VALUES },
  priority: { type: "string", required: false, enum: PRIORITY_VALUES },
  category: { type: "string", required: false, min: 2, max: 60 },
  due_date: { type: "number", required: false, min: 0 },
};

function parseQueryList(input) {
  if (!input) {
    return null;
  }
  const values = Array.isArray(input) ? input : [input];
  const normalized = values
    .flatMap((value) => String(value).split(","))
    .map((value) => value.trim())
    .filter(Boolean);
  return normalized.length ? normalized : null;
}

function applyTaskFilters(tasks, query) {
  let filtered = [...tasks];

  const statuses = parseQueryList(query.status);
  if (statuses) {
    filtered = filtered.filter((task) => statuses.includes(task.status));
  }

  const priorities = parseQueryList(query.priority);
  if (priorities) {
    filtered = filtered.filter((task) => priorities.includes(task.priority));
  }

  const categories = parseQueryList(query.category);
  if (categories) {
    filtered = filtered.filter((task) => categories.includes(task.category));
  }

  if (query.search) {
    const term = String(query.search).toLowerCase().trim();
    if (term) {
      filtered = filtered.filter((task) => {
        const haystack = `${task.title} ${task.description ?? ""}`.toLowerCase();
        return haystack.includes(term);
      });
    }
  }

  return filtered;
}

function sortTasks(tasks, sortKey) {
  const output = [...tasks];
  const priorityRank = { low: 0, medium: 1, high: 2, critical: 3 };
  const statusRank = { todo: 0, in_progress: 1, done: 2, archived: 3 };

  switch (sortKey) {
    case "created_asc":
      output.sort((a, b) => a.created_at - b.created_at);
      break;
    case "updated_asc":
      output.sort((a, b) => a.updated_at - b.updated_at);
      break;
    case "updated_desc":
      output.sort((a, b) => b.updated_at - a.updated_at);
      break;
    case "due_asc":
      output.sort((a, b) => (a.due_date ?? Number.MAX_SAFE_INTEGER) - (b.due_date ?? Number.MAX_SAFE_INTEGER));
      break;
    case "due_desc":
      output.sort((a, b) => (b.due_date ?? 0) - (a.due_date ?? 0));
      break;
    case "priority":
      output.sort((a, b) => priorityRank[b.priority] - priorityRank[a.priority]);
      break;
    case "status":
      output.sort((a, b) => statusRank[a.status] - statusRank[b.status]);
      break;
    case "created_desc":
    default:
      output.sort((a, b) => b.created_at - a.created_at);
      break;
  }

  return output;
}

function hasPatchData(body) {
  const keys = Object.keys(body ?? {});
  return keys.some((key) => updateTaskSchema[key]);
}

function createAuditEntry({ userId, action, resourceId, detail, timestamp }) {
  return {
    id: generateUUID(),
    user_id: userId,
    action,
    resource_id: resourceId,
    detail: JSON.stringify(detail ?? {}),
    timestamp,
  };
}

export function registerTaskRoutes(router, { db, requireAuth, apiRateLimit }) {
  router.get("/api/tasks", requireAuth, apiRateLimit("tasks:list"), async (req) => {
    const userTasks = await db.getAll("tasks", {
      index: "user_id",
      range: IDBKeyRange.only(req.user.id),
    });

    const activeTasks = userTasks.filter((task) => !task.deleted_at);
    const filtered = applyTaskFilters(activeTasks, req.query);
    const sorted = sortTasks(filtered, req.query.sort);

    const page = Math.max(1, Math.floor(safeNumber(req.query.page, 1)));
    const limit = Math.max(1, Math.min(100, Math.floor(safeNumber(req.query.limit, 20))));
    const startIndex = (page - 1) * limit;
    const paginated = sorted.slice(startIndex, startIndex + limit);

    return successResponse(paginated, {
      meta: {
        page,
        limit,
        total: sorted.length,
      },
    });
  });

  router.post(
    "/api/tasks",
    requireAuth,
    apiRateLimit("tasks:create"),
    validate(createTaskSchema, { allowUnknown: false }),
    async (req) => {
      const now = Date.now();
      const status = req.body.status ?? "todo";
      const task = {
        id: generateUUID(),
        user_id: req.user.id,
        title: req.body.title.trim(),
        description: req.body.description?.trim() ?? "",
        status,
        priority: req.body.priority ?? "medium",
        category: req.body.category?.trim() || "general",
        due_date: req.body.due_date ?? null,
        created_at: now,
        updated_at: now,
        completed_at: status === "done" ? now : null,
      };

      const auditEntry = createAuditEntry({
        userId: req.user.id,
        action: "task.create",
        resourceId: task.id,
        detail: { status: task.status, priority: task.priority, category: task.category },
        timestamp: now,
      });

      await db.transaction(["tasks", "audit_log"], "readwrite", (stores) => {
        stores.tasks.put(task);
        stores.audit_log.put(auditEntry);
      });

      return successResponse(task, { status: 201 });
    },
  );

  router.put(
    "/api/tasks/:id",
    requireAuth,
    apiRateLimit("tasks:update"),
    validate(updateTaskSchema, { allowUnknown: false }),
    async (req) => {
      if (!hasPatchData(req.body)) {
        return errorResponse(400, "At least one valid field is required for update");
      }

      const task = await db.get("tasks", req.params.id);
      if (!task || task.deleted_at) {
        return errorResponse(404, "Task not found");
      }
      if (task.user_id !== req.user.id) {
        return errorResponse(403, "You do not have permission to modify this task");
      }

      const now = Date.now();
      const nextStatus = req.body.status ?? task.status;
      let completedAt = task.completed_at;
      if (nextStatus === "done" && !completedAt) {
        completedAt = now;
      } else if (nextStatus !== "done") {
        completedAt = null;
      }

      const updatedTask = {
        ...task,
        ...req.body,
        title: req.body.title?.trim() ?? task.title,
        description: req.body.description?.trim() ?? task.description,
        category: req.body.category?.trim() ?? task.category,
        status: nextStatus,
        updated_at: now,
        completed_at: completedAt,
      };

      const auditEntry = createAuditEntry({
        userId: req.user.id,
        action: "task.update",
        resourceId: updatedTask.id,
        detail: req.body,
        timestamp: now,
      });

      await db.transaction(["tasks", "audit_log"], "readwrite", (stores) => {
        stores.tasks.put(updatedTask);
        stores.audit_log.put(auditEntry);
      });

      return successResponse(updatedTask);
    },
  );

  router.delete("/api/tasks/:id", requireAuth, apiRateLimit("tasks:delete"), async (req) => {
    const task = await db.get("tasks", req.params.id);
    if (!task || task.deleted_at) {
      return errorResponse(404, "Task not found");
    }
    if (task.user_id !== req.user.id) {
      return errorResponse(403, "You do not have permission to delete this task");
    }

    const now = Date.now();
    const hardDelete = String(req.query.hard ?? "").toLowerCase() === "true";
    const auditEntry = createAuditEntry({
      userId: req.user.id,
      action: "task.delete",
      resourceId: task.id,
      detail: { hard: hardDelete },
      timestamp: now,
    });

    await db.transaction(["tasks", "audit_log"], "readwrite", (stores) => {
      if (hardDelete) {
        stores.tasks.delete(task.id);
      } else {
        stores.tasks.put({
          ...task,
          status: "archived",
          deleted_at: now,
          updated_at: now,
        });
      }
      stores.audit_log.put(auditEntry);
    });

    return successResponse({
      id: task.id,
      deleted: true,
      hard: hardDelete,
    });
  });
}

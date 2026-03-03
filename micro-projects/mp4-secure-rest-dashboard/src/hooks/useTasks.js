import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext.jsx";

const DEFAULT_FILTERS = {
  status: [],
  priority: "",
  category: "",
  search: "",
  sort: "created_desc",
  page: 1,
  limit: 20,
};

function buildQueryString(filters) {
  const params = new URLSearchParams();
  if (filters.status.length > 0) {
    params.set("status", filters.status.join(","));
  }
  if (filters.priority) {
    params.set("priority", filters.priority);
  }
  if (filters.category) {
    params.set("category", filters.category.trim());
  }
  if (filters.search) {
    params.set("search", filters.search.trim());
  }
  params.set("sort", filters.sort);
  params.set("page", String(filters.page));
  params.set("limit", String(filters.limit));
  return params.toString();
}

export function useTasks() {
  const { apiFetch } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState(DEFAULT_FILTERS);

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const query = buildQueryString(filters);
      const response = await apiFetch(`/api/tasks?${query}`);
      setTasks(response?.data ?? []);
    } catch (requestError) {
      setError(requestError.message ?? "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }, [apiFetch, filters]);

  useEffect(() => {
    void loadTasks();
  }, [loadTasks]);

  const createTask = useCallback(
    async (payload) => {
      const optimisticTask = {
        id: `tmp-${Date.now()}`,
        user_id: "me",
        title: payload.title,
        description: payload.description ?? "",
        status: payload.status ?? "todo",
        priority: payload.priority ?? "medium",
        category: payload.category ?? "general",
        due_date: payload.due_date ?? null,
        created_at: Date.now(),
        updated_at: Date.now(),
        completed_at: payload.status === "done" ? Date.now() : null,
        __optimistic: true,
      };

      const snapshot = tasks;
      setTasks((previous) => [optimisticTask, ...previous]);
      setError("");

      try {
        const response = await apiFetch("/api/tasks", {
          method: "POST",
          body: payload,
        });
        const createdTask = response?.data;
        setTasks((previous) => previous.map((task) => (task.id === optimisticTask.id ? createdTask : task)));
        return createdTask;
      } catch (requestError) {
        setTasks(snapshot);
        setError(requestError.message ?? "Failed to create task");
        throw requestError;
      }
    },
    [apiFetch, tasks],
  );

  const updateTask = useCallback(
    async (taskId, patch) => {
      const snapshot = tasks;
      setTasks((previous) =>
        previous.map((task) =>
          task.id === taskId
            ? {
                ...task,
                ...patch,
                updated_at: Date.now(),
              }
            : task,
        ),
      );
      setError("");

      try {
        const response = await apiFetch(`/api/tasks/${taskId}`, {
          method: "PUT",
          body: patch,
        });
        const updatedTask = response?.data;
        setTasks((previous) => previous.map((task) => (task.id === taskId ? updatedTask : task)));
        return updatedTask;
      } catch (requestError) {
        setTasks(snapshot);
        setError(requestError.message ?? "Failed to update task");
        throw requestError;
      }
    },
    [apiFetch, tasks],
  );

  const deleteTask = useCallback(
    async (taskId) => {
      const snapshot = tasks;
      setTasks((previous) => previous.filter((task) => task.id !== taskId));
      setError("");

      try {
        await apiFetch(`/api/tasks/${taskId}`, { method: "DELETE" });
      } catch (requestError) {
        setTasks(snapshot);
        setError(requestError.message ?? "Failed to delete task");
        throw requestError;
      }
    },
    [apiFetch, tasks],
  );

  return {
    tasks,
    loading,
    error,
    filters,
    setFilters,
    createTask,
    updateTask,
    deleteTask,
    reloadTasks: loadTasks,
  };
}

import { useCallback, useMemo, useState } from "react";
import { useAuth } from "../contexts/AuthContext.jsx";
import { useTasks } from "../hooks/useTasks.js";
import FilterBar from "../components/FilterBar.jsx";
import TaskCard from "../components/TaskCard.jsx";
import TaskForm from "../components/TaskForm.jsx";
import styles from "./TasksPage.module.css";

const DEFAULT_FILTERS = {
  status: [],
  priority: "",
  category: "",
  search: "",
  sort: "created_desc",
  page: 1,
  limit: 20,
};

function TasksPage() {
  const { user, logout } = useAuth();
  const { tasks, loading, error, filters, setFilters, createTask, updateTask, deleteTask } = useTasks();
  const [showCreateForm, setShowCreateForm] = useState(false);

  const taskCountLabel = useMemo(() => `${tasks.length} task${tasks.length === 1 ? "" : "s"}`, [tasks.length]);

  const handleFilterChange = useCallback(
    (nextFilters) => {
      setFilters(nextFilters);
    },
    [setFilters],
  );

  const handleClearFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, [setFilters]);

  const handleCreateTask = useCallback(
    async (payload) => {
      await createTask(payload);
      setShowCreateForm(false);
    },
    [createTask],
  );

  const handleUpdateTask = useCallback(
    async (taskId, payload) => {
      await updateTask(taskId, payload);
    },
    [updateTask],
  );

  const handleDeleteTask = useCallback(
    async (taskId) => {
      await deleteTask(taskId);
    },
    [deleteTask],
  );

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <div>
          <h2>Task Workspace</h2>
          <p>
            Signed in as <strong>{user?.username}</strong> · {taskCountLabel}
          </p>
        </div>
        <div className={styles.headerActions}>
          <button type="button" className={styles.primaryButton} onClick={() => setShowCreateForm((prev) => !prev)}>
            {showCreateForm ? "Close" : "Add Task"}
          </button>
          <button type="button" className={styles.secondaryButton} onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <FilterBar filters={filters} onChange={handleFilterChange} onClear={handleClearFilters} />

      {showCreateForm && (
        <section className={`card ${styles.createPanel}`} aria-label="Create task">
          <h3>Create a New Task</h3>
          <TaskForm onSubmit={handleCreateTask} onCancel={() => setShowCreateForm(false)} submitLabel="Create Task" />
        </section>
      )}

      {error && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}

      {loading ? (
        <p className={styles.loading}>Loading tasks...</p>
      ) : tasks.length === 0 ? (
        <div className={`card ${styles.emptyState}`}>
          <h3>No tasks match your filters</h3>
          <p>Try clearing filters or create a new task.</p>
        </div>
      ) : (
        <div className={styles.list}>
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onUpdate={handleUpdateTask} onDelete={handleDeleteTask} />
          ))}
        </div>
      )}
    </section>
  );
}

export default TasksPage;

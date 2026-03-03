import { useEffect, useState } from "react";
import styles from "./TaskForm.module.css";

const STATUS_OPTIONS = [
  { label: "To Do", value: "todo" },
  { label: "In Progress", value: "in_progress" },
  { label: "Done", value: "done" },
  { label: "Archived", value: "archived" },
];

const PRIORITY_OPTIONS = [
  { label: "Low", value: "low" },
  { label: "Medium", value: "medium" },
  { label: "High", value: "high" },
  { label: "Critical", value: "critical" },
];

function toDateInputValue(timestamp) {
  if (!timestamp) {
    return "";
  }
  const date = new Date(timestamp);
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function createInitialState(initialData) {
  return {
    title: initialData?.title ?? "",
    description: initialData?.description ?? "",
    status: initialData?.status ?? "todo",
    priority: initialData?.priority ?? "medium",
    category: initialData?.category ?? "general",
    dueDate: toDateInputValue(initialData?.due_date),
  };
}

function TaskForm({ initialData, onSubmit, onCancel, submitLabel = "Save Task" }) {
  const [form, setForm] = useState(() => createInitialState(initialData));
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setForm(createInitialState(initialData));
    setError("");
  }, [initialData]);

  const handleFieldChange = (event) => {
    const { name, value } = event.target;
    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!form.title.trim()) {
      setError("Title is required.");
      return;
    }
    if (form.title.trim().length > 140) {
      setError("Title must be at most 140 characters.");
      return;
    }

    const payload = {
      title: form.title.trim(),
      description: form.description.trim(),
      status: form.status,
      priority: form.priority,
      category: form.category.trim() || "general",
    };

    if (form.dueDate) {
      payload.due_date = new Date(`${form.dueDate}T00:00:00`).getTime();
    }

    try {
      setIsSubmitting(true);
      await onSubmit(payload);
    } catch (submitError) {
      setError(submitError.message ?? "Unable to save task.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.field}>
        <label htmlFor="task-title">Title</label>
        <input
          id="task-title"
          name="title"
          type="text"
          maxLength={140}
          value={form.title}
          onChange={handleFieldChange}
          required
        />
      </div>

      <div className={styles.field}>
        <label htmlFor="task-description">Description</label>
        <textarea
          id="task-description"
          name="description"
          rows={3}
          value={form.description}
          onChange={handleFieldChange}
        />
      </div>

      <div className={styles.grid}>
        <div className={styles.field}>
          <label htmlFor="task-status">Status</label>
          <select id="task-status" name="status" value={form.status} onChange={handleFieldChange}>
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.field}>
          <label htmlFor="task-priority">Priority</label>
          <select id="task-priority" name="priority" value={form.priority} onChange={handleFieldChange}>
            {PRIORITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.field}>
          <label htmlFor="task-category">Category</label>
          <input
            id="task-category"
            name="category"
            type="text"
            maxLength={60}
            value={form.category}
            onChange={handleFieldChange}
          />
        </div>

        <div className={styles.field}>
          <label htmlFor="task-due-date">Due Date</label>
          <input id="task-due-date" name="dueDate" type="date" value={form.dueDate} onChange={handleFieldChange} />
        </div>
      </div>

      {error && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}

      <div className={styles.actions}>
        <button className={styles.submitButton} type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitLabel}
        </button>
        {onCancel && (
          <button className={styles.cancelButton} type="button" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default TaskForm;

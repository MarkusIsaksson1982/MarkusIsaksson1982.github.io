import { memo, useState } from "react";
import TaskForm from "./TaskForm.jsx";
import styles from "./TaskCard.module.css";

function formatDate(timestamp) {
  if (!timestamp) {
    return "No due date";
  }
  return new Date(timestamp).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

const TaskCard = memo(function TaskCard({ task, onUpdate, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState(false);

  const handleDelete = async () => {
    const confirmed = window.confirm(`Delete task "${task.title}"?`);
    if (!confirmed) {
      return;
    }
    await onDelete(task.id);
  };

  const handleEditSave = async (payload) => {
    await onUpdate(task.id, payload);
    setEditing(false);
  };

  return (
    <article className={`card ${styles.card}`} aria-labelledby={`task-title-${task.id}`}>
      <button
        className={styles.summary}
        type="button"
        onClick={() => setExpanded((current) => !current)}
        aria-expanded={expanded}
      >
        <div className={styles.heading}>
          <h3 id={`task-title-${task.id}`}>{task.title}</h3>
          <div className={styles.badges}>
            <span className={`${styles.badge} ${styles[`status_${task.status}`]}`}>{task.status}</span>
            <span className={`${styles.badge} ${styles[`priority_${task.priority}`]}`}>{task.priority}</span>
          </div>
        </div>
        <p className={styles.meta}>
          <span>{task.category}</span>
          <span>Due: {formatDate(task.due_date)}</span>
        </p>
      </button>

      {expanded && (
        <div className={styles.expanded}>
          {task.description && <p className={styles.description}>{task.description}</p>}

          {editing ? (
            <TaskForm
              initialData={task}
              onSubmit={handleEditSave}
              onCancel={() => setEditing(false)}
              submitLabel="Update Task"
            />
          ) : (
            <div className={styles.actions}>
              <button className={styles.actionPrimary} type="button" onClick={() => setEditing(true)}>
                Edit
              </button>
              <button className={styles.actionDanger} type="button" onClick={handleDelete}>
                Delete
              </button>
            </div>
          )}
        </div>
      )}
    </article>
  );
});

export default TaskCard;

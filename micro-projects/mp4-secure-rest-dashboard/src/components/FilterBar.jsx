import styles from "./FilterBar.module.css";

const STATUS_OPTIONS = [
  { label: "To Do", value: "todo" },
  { label: "In Progress", value: "in_progress" },
  { label: "Done", value: "done" },
  { label: "Archived", value: "archived" },
];

const SORT_OPTIONS = [
  { label: "Newest first", value: "created_desc" },
  { label: "Oldest first", value: "created_asc" },
  { label: "Recently updated", value: "updated_desc" },
  { label: "Due date", value: "due_asc" },
  { label: "Priority", value: "priority" },
  { label: "Status", value: "status" },
];

function FilterBar({ filters, onChange, onClear }) {
  const handleStatusToggle = (statusValue) => {
    const exists = filters.status.includes(statusValue);
    const nextStatus = exists
      ? filters.status.filter((value) => value !== statusValue)
      : [...filters.status, statusValue];

    onChange({
      ...filters,
      status: nextStatus,
      page: 1,
    });
  };

  const handleFieldChange = (event) => {
    const { name, value } = event.target;
    onChange({
      ...filters,
      [name]: value,
      page: 1,
    });
  };

  return (
    <section className={`card ${styles.wrapper}`} aria-label="Task filters">
      <div className={styles.group}>
        <p className={styles.groupLabel}>Status</p>
        <div className={styles.statusList}>
          {STATUS_OPTIONS.map((statusOption) => (
            <label className={styles.statusItem} key={statusOption.value}>
              <input
                type="checkbox"
                checked={filters.status.includes(statusOption.value)}
                onChange={() => handleStatusToggle(statusOption.value)}
              />
              <span>{statusOption.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className={styles.group}>
        <label className={styles.label} htmlFor="filter-priority">
          Priority
        </label>
        <select id="filter-priority" name="priority" value={filters.priority} onChange={handleFieldChange}>
          <option value="">All priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      <div className={styles.group}>
        <label className={styles.label} htmlFor="filter-category">
          Category
        </label>
        <input
          id="filter-category"
          name="category"
          type="text"
          placeholder="e.g. development"
          value={filters.category}
          onChange={handleFieldChange}
        />
      </div>

      <div className={styles.group}>
        <label className={styles.label} htmlFor="filter-search">
          Search
        </label>
        <input
          id="filter-search"
          name="search"
          type="search"
          placeholder="Search title or description"
          value={filters.search}
          onChange={handleFieldChange}
        />
      </div>

      <div className={styles.group}>
        <label className={styles.label} htmlFor="filter-sort">
          Sort
        </label>
        <select id="filter-sort" name="sort" value={filters.sort} onChange={handleFieldChange}>
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.actions}>
        <button className={styles.clearButton} type="button" onClick={onClear}>
          Clear Filters
        </button>
      </div>
    </section>
  );
}

export default FilterBar;

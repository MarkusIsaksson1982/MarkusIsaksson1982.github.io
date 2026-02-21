import styles from './EmptyState.module.css';

/**
 * EmptyState — shown when no certifications match current filters.
 * @param {{ onClearFilters: () => void }} props
 */
export default function EmptyState({ onClearFilters }) {
  return (
    <div className={styles.emptyState} aria-live="polite">
      <p className={styles.emoji} aria-hidden="true">🔍</p>
      <p className={styles.text}>No certifications match your current filters.</p>
      <button className={styles.clearBtn} onClick={onClearFilters} type="button">
        Clear all filters
      </button>
    </div>
  );
}

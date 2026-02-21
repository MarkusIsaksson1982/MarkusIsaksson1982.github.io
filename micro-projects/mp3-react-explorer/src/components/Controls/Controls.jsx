import { useState, useCallback, useEffect, memo } from 'react';
import { useDebounce } from '../../hooks/useDebounce';
import styles from './Controls.module.css';

/**
 * Tag — individual tech tag button. Memoized independently so the entire
 * TagCloud doesn't re-render when one tag changes active state.
 */
const Tag = memo(function Tag({ tag, isActive, onToggle }) {
  return (
    <button
      className={`${styles.tag} ${isActive ? styles.tagActive : ''}`}
      onClick={() => onToggle(tag)}
      aria-pressed={isActive}
      type="button"
    >
      {tag}
    </button>
  );
});

/**
 * Controls — search input, category dropdown, tech tag multi-select.
 *
 * Search uses local state + useDebounce to avoid dispatching on every keystroke.
 * The debounced value is dispatched to AppContext (triggers filter recompute).
 * The input displays the local (immediate) value for responsive feel.
 *
 * @param {{ query, category, activeTags, allTags, dispatch }} props
 */
const Controls = memo(function Controls({
  query,
  category,
  activeTags,
  allTags,
  dispatch,
}) {
  // Local input state for immediate visual feedback (no dispatch delay)
  const [localQuery, setLocalQuery] = useState(query);

  // Debounced value — dispatched to context after 200ms of inactivity
  const debouncedQuery = useDebounce(localQuery, 200);

  // Sync debounced value to AppContext after 200ms of typing inactivity
  // useEffect runs when debouncedQuery changes — the 200ms delay comes from useDebounce
  useEffect(() => {
    dispatch({ type: 'SET_QUERY', payload: debouncedQuery });
  }, [debouncedQuery, dispatch]);

  const handleSearchChange = useCallback((e) => {
    setLocalQuery(e.target.value);
  }, []);

  const handleCategoryChange = useCallback((e) => {
    dispatch({ type: 'SET_CATEGORY', payload: e.target.value });
  }, [dispatch]);

  const handleTagToggle = useCallback((tag) => {
    dispatch({ type: 'TOGGLE_TAG', payload: tag });
  }, [dispatch]);

  return (
    <section className={styles.controls} aria-label="Filter certifications">
      <div className={styles.inner}>
        <div className={styles.controlsTop}>
          <div className={styles.searchWrapper}>
            <label htmlFor="cert-search" className="visually-hidden">
              Search by name or skill
            </label>
            <span className={styles.searchIcon} aria-hidden="true">⌕</span>
            <input
              type="search"
              id="cert-search"
              className={styles.searchInput}
              value={localQuery}
              onChange={handleSearchChange}
              placeholder="Search certifications or skills…"
              autoComplete="off"
              aria-controls="cert-grid"
            />
          </div>

          <label htmlFor="category-filter" className="visually-hidden">
            Filter by category
          </label>
          <select
            id="category-filter"
            className={styles.categorySelect}
            value={category}
            onChange={handleCategoryChange}
            aria-controls="cert-grid"
          >
            <option value="all">All Categories</option>
            <option value="legacy">Legacy Curriculum</option>
            <option value="new">New Curriculum</option>
            <option value="additional">Additional</option>
          </select>
        </div>

        <div
          className={styles.tagCloud}
          role="group"
          aria-label="Filter by technology — multi-select"
        >
          {allTags.map(tag => (
            <Tag
              key={tag}
              tag={tag}
              isActive={activeTags.has(tag)}
              onToggle={handleTagToggle}
            />
          ))}
        </div>
      </div>
    </section>
  );
});

export default Controls;

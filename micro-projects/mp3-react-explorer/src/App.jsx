import { useCallback, useMemo } from 'react';
import { useAppState } from './context/AppContext';
import { useFilteredCerts } from './hooks/useFilteredCerts';
import { CERTIFICATIONS } from './data/certifications';
import { getAllTags } from './utils/helpers';
import Header from './components/Header/Header';
import StatsBar from './components/StatsBar/StatsBar';
import Controls from './components/Controls/Controls';
import CertGrid from './components/CertGrid/CertGrid';
import EmptyState from './components/EmptyState/EmptyState';
import Modal from './components/Modal/Modal';
import Footer from './components/Footer/Footer';
import styles from './App.module.css';

/**
 * App — layout shell and data coordinator.
 *
 * Responsibilities:
 * - Read AppContext (state + dispatch)
 * - Derive filteredCerts (via custom hook)
 * - Create stable callbacks (useCallback) for child components
 * - Route data to the right components
 * - Conditionally render Modal
 *
 * Does NOT: own state, render UI details, make decisions about visuals.
 * Every visual decision lives in a named component.
 */
export default function App() {
  const { state, dispatch } = useAppState();
  const { query, category, activeTags, openSlug, notes } = state;

  /**
   * Memoized filtered certifications.
   * Stable reference → React.memo(CertCard) never re-renders during filtering.
   */
  const filteredCerts = useFilteredCerts(CERTIFICATIONS, query, category, activeTags);

  /**
   * All unique tech tags — stable because CERTIFICATIONS never changes.
   * useMemo with empty-ish deps: only recomputes if certs array reference changes (never).
   */
  const allTags = useMemo(() => getAllTags(CERTIFICATIONS), []);

  /**
   * useCallback on all handlers passed to React.memo children.
   * Without useCallback, a new function reference every render breaks memo.
   * dispatch is stable (guaranteed by useReducer) — safe as sole dep.
   */
  const handleCardClick = useCallback(
    (slug) => dispatch({ type: 'OPEN_MODAL', payload: slug }),
    [dispatch]
  );

  const handleCloseModal = useCallback(
    () => dispatch({ type: 'CLOSE_MODAL' }),
    [dispatch]
  );

  const handleSaveNote = useCallback(
    (slug, text) => dispatch({ type: 'SAVE_NOTE', payload: { slug, text } }),
    [dispatch]
  );

  const handleClearFilters = useCallback(
    () => dispatch({ type: 'CLEAR_FILTERS' }),
    [dispatch]
  );

  // Resolve open cert object — null when no modal is open
  const openCert = openSlug ? CERTIFICATIONS.find(c => c.slug === openSlug) : null;

  return (
    <>
      <a href="#main-content" className="skip-link">Skip to main content</a>

      <Header />

      <StatsBar
        filteredCerts={filteredCerts}
        totalCerts={CERTIFICATIONS.length}
      />

      <Controls
        query={query}
        category={category}
        activeTags={activeTags}
        allTags={allTags}
        dispatch={dispatch}
      />

      <main id="main-content" className={styles.main}>
        {/* Screen reader live region — announces filter results */}
        <div
          className="visually-hidden"
          aria-live="polite"
          aria-atomic="true"
        >
          {filteredCerts.length > 0
            ? `${filteredCerts.length} certification${filteredCerts.length !== 1 ? 's' : ''} found`
            : 'No certifications match your current filters'}
        </div>

        {filteredCerts.length < CERTIFICATIONS.length && (
          <p className={styles.resultsMeta} aria-live="polite">
            Showing {filteredCerts.length} of {CERTIFICATIONS.length} certifications
          </p>
        )}

        {filteredCerts.length > 0 ? (
          <CertGrid certs={filteredCerts} onCardClick={handleCardClick} />
        ) : (
          <EmptyState onClearFilters={handleClearFilters} />
        )}
      </main>

      {/* Modal — conditionally rendered (not hidden with CSS) so focus
          lifecycle effects run correctly on mount/unmount */}
      {openCert && (
        <Modal
          cert={openCert}
          note={notes[openCert.slug] || ''}
          onClose={handleCloseModal}
          onSaveNote={handleSaveNote}
        />
      )}

      <Footer />
    </>
  );
}

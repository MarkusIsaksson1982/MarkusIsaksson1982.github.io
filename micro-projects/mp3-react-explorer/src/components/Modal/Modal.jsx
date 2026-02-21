import { useRef, useEffect, useCallback, useState } from 'react';
import { getCategoryLabel } from '../../utils/helpers';
import styles from './Modal.module.css';

const FOCUSABLE_SELECTORS =
  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

/**
 * Modal — certification detail view.
 *
 * React lifecycle gives us clean focus management:
 *
 * Mount  → focus close button, lock body scroll
 * Unmount → restore prior focus, unlock scroll
 *
 * This is cleaner than MP1's imperative focusTrap() because React's
 * useEffect cleanup function runs at exactly the right moment.
 *
 * Conditional rendering (not display:none) ensures effects run on
 * mount/unmount — hiding with CSS would prevent cleanup from running.
 *
 * @param {{ cert, note, onClose, onSaveNote }} props
 */
export default function Modal({ cert, note, onClose, onSaveNote }) {
  const closeRef = useRef(null);
  const overlayRef = useRef(null);
  const [localNote, setLocalNote] = useState(note);
  const [savedIndicator, setSavedIndicator] = useState('');
  const savedTimerRef = useRef(null);

  // ── Focus close button + lock scroll on mount ──────────────────
  useEffect(() => {
    closeRef.current?.focus();
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = ''; // Cleanup: unlock on unmount ✓
    };
  }, []); // Empty deps: runs once on mount

  // ── Restore focus to triggering element on unmount ─────────────
  useEffect(() => {
    const trigger = document.activeElement;
    return () => trigger?.focus(); // Cleanup: return focus on unmount ✓
  }, []);

  // ── Escape key close ───────────────────────────────────────────
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey); // Cleanup ✓
  }, [onClose]);

  // ── Focus trap (Tab cycling within modal) ─────────────────────
  useEffect(() => {
    const handleTab = (e) => {
      if (e.key !== 'Tab') return;
      const modal = overlayRef.current?.querySelector('[role="dialog"]');
      if (!modal) return;
      const focusable = [...modal.querySelectorAll(FOCUSABLE_SELECTORS)];
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) { e.preventDefault(); last.focus(); }
      } else {
        if (document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab); // Cleanup ✓
  }, []);

  // ── Overlay click to close ─────────────────────────────────────
  const handleOverlayClick = useCallback((e) => {
    if (e.target === overlayRef.current) onClose();
  }, [onClose]);

  // ── Note save ─────────────────────────────────────────────────
  const handleNoteChange = useCallback((e) => {
    const text = e.target.value;
    setLocalNote(text);
    onSaveNote(cert.slug, text);
    setSavedIndicator('✓ Saved');
    clearTimeout(savedTimerRef.current);
    savedTimerRef.current = setTimeout(() => setSavedIndicator(''), 2000);
  }, [cert.slug, onSaveNote]);

  // Cleanup saved indicator timer on unmount
  useEffect(() => {
    return () => clearTimeout(savedTimerRef.current); // Cleanup ✓
  }, []);

  return (
    <div
      ref={overlayRef}
      className={styles.overlay}
      onClick={handleOverlayClick}
    >
      <div
        className={styles.modal}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <button
          ref={closeRef}
          className={styles.closeBtn}
          onClick={onClose}
          aria-label="Close certification detail"
        >
          ✕
        </button>

        <div className={styles.content}>
          {/* Header */}
          <div className={styles.modalHeader}>
            <span className={styles.modalIcon} aria-hidden="true">{cert.icon}</span>
            <div>
              <h2 className={styles.modalTitle} id="modal-title">{cert.name}</h2>
              <div className={styles.modalMeta}>
                <span className={styles.hoursBadge}>
                  ⏱ {cert.approxHours.toLocaleString()}h
                </span>
                <span className={`${styles.catBadge} ${styles[cert.category]}`}>
                  {getCategoryLabel(cert.category)}
                </span>
              </div>
            </div>
          </div>

          {/* Skills */}
          <section aria-label="Skills and technologies">
            <h3 className={styles.sectionTitle}>Skills & Technologies</h3>
            <ul className={styles.skillsList} role="list">
              {cert.skills.map(skill => (
                <li key={skill} role="listitem">
                  <span className={styles.skillTag}>{skill}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Engineering insight */}
          <section aria-label="Engineering insight">
            <h3 className={styles.sectionTitle}>Engineering Insight</h3>
            <p className={styles.noteText}>{cert.note}</p>
          </section>

          {/* Personal reflection */}
          <section aria-label="Personal reflection">
            <h3 className={styles.sectionTitle}>
              My Reflection
              <span className={styles.autoSaveLabel}>(auto-saved)</span>
            </h3>
            <label htmlFor="modal-note" className="visually-hidden">
              Personal notes for {cert.name}
            </label>
            <textarea
              id="modal-note"
              className={styles.textarea}
              value={localNote}
              onChange={handleNoteChange}
              placeholder="Write your reflections, project ideas, or next steps…"
              rows={4}
            />
            <p
              className={styles.saveIndicator}
              aria-live="polite"
              aria-atomic="true"
            >
              {savedIndicator}
            </p>
          </section>

          {/* Actions */}
          <div className={styles.modalActions}>
            <a
              href={cert.url}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.primaryBtn}
              aria-label={`View ${cert.name} certificate on freeCodeCamp (opens in new tab)`}
            >
              View Certificate ↗
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

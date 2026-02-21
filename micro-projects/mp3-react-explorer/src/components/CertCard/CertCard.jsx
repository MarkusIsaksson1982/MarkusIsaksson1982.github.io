import { memo } from 'react';
import { useIntersectionObserver } from '../../hooks/useIntersectionObserver';
import { getCategoryLabel } from '../../utils/helpers';
import styles from './CertCard.module.css';

/**
 * CertCard — React.memo prevents re-render when cert + onClick are unchanged.
 *
 * Re-render analysis:
 * - cert: from CERTIFICATIONS static array — same object reference always ✓
 * - onClick: wrapped in useCallback(dispatch) in App.jsx — stable reference ✓
 * → Cards render ONCE and never re-render. Filtering changes which cards
 *   are in the DOM (React reconciles the list), but surviving cards stay frozen.
 *
 * This is the React equivalent of MP1's simpleHash() reconciliation —
 * except React's virtual DOM does it automatically, and React.memo lets
 * us declare explicitly that a component should be treated as pure.
 *
 * @param {{ cert: import('../../data/certifications').Certification, onClick: Function }} props
 */
const CertCard = memo(function CertCard({ cert, onClick }) {
  // Entrance animation: adds styles.visible when card scrolls into view
  // useIntersectionObserver returns a ref — attach to the article element
  const cardRef = useIntersectionObserver(styles.visible);

  const catBadgeClass = {
    legacy: styles.badgeLegacy,
    new: styles.badgeNew,
    additional: styles.badgeAdditional,
  }[cert.category] || '';

  const cardCatClass = {
    legacy: styles.cardLegacy,
    new: styles.cardNew,
    additional: styles.cardAdditional,
  }[cert.category] || '';

  return (
    <article
      ref={cardRef}
      className={`${styles.card} ${cardCatClass}`}
      role="listitem"
      tabIndex={0}
      onClick={() => onClick(cert.slug)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick(cert.slug);
        }
      }}
      aria-label={`View details for ${cert.name}`}
    >
      <div className={styles.cardHeader}>
        <span className={styles.icon} aria-hidden="true">{cert.icon}</span>
        <span className={`${styles.badge} ${catBadgeClass}`}>
          {getCategoryLabel(cert.category)}
        </span>
      </div>

      <h2 className={styles.title}>{cert.name}</h2>

      <span className={styles.hoursBadge} aria-label={`${cert.approxHours} hours of study`}>
        ⏱ {cert.approxHours.toLocaleString()}h
      </span>

      <div
        className={styles.progressTrack}
        role="progressbar"
        aria-valuenow={100}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${cert.name}: completed`}
      >
        <div className={styles.progressFill} />
      </div>

      <div className={styles.tags} aria-label="Skills covered">
        {cert.skills.slice(0, 4).map(skill => (
          <span key={skill} className={styles.tag}>{skill}</span>
        ))}
        {cert.skills.length > 4 && (
          <span className={`${styles.tag} ${styles.tagMore}`}>
            +{cert.skills.length - 4}
          </span>
        )}
      </div>

      <div className={styles.cardFooter}>
        <span className={styles.status}>✓ Completed</span>
        <span className={styles.viewHint} aria-hidden="true">Details →</span>
      </div>
    </article>
  );
});

export default CertCard;

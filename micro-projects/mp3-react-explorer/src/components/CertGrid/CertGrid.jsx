import { memo } from 'react';
import CertCard from '../CertCard/CertCard';
import styles from './CertGrid.module.css';

/**
 * CertGrid — maps filtered certifications to CertCard components.
 *
 * React.memo: re-renders only when certs array reference or onCardClick changes.
 * certs: stable when filters haven't changed (memoized in App via useFilteredCerts)
 * onCardClick: stable (useCallback in App)
 * → In practice, CertGrid re-renders only when filters actually change.
 *
 * Key prop: cert.slug — stable, meaningful, never an array index.
 * Using index as key would cause React to reuse wrong DOM nodes on reorder.
 *
 * @param {{ certs: Array, onCardClick: (slug: string) => void }} props
 */
const CertGrid = memo(function CertGrid({ certs, onCardClick }) {
  return (
    <div
      className={styles.grid}
      id="cert-grid"
      role="list"
      aria-label="Certification cards"
    >
      {certs.map(cert => (
        <CertCard
          key={cert.slug}       // slug: stable, meaningful key ✓
          cert={cert}
          onClick={onCardClick}
        />
      ))}
    </div>
  );
});

export default CertGrid;

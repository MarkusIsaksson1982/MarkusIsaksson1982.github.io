import { useEffect, useRef, memo } from 'react';
import { getStats } from '../../utils/helpers';
import styles from './StatsBar.module.css';

/**
 * AnimatedCount — renders a count-up animation when value changes.
 * Uses useRef to track the animation frame ID for proper cleanup.
 *
 * @param {{ value: number, label: string }} props
 */
const AnimatedCount = memo(function AnimatedCount({ value, label }) {
  const elRef = useRef(null);
  const prevRef = useRef(0);

  useEffect(() => {
    const el = elRef.current;
    if (!el) return;

    const start = prevRef.current;
    const end = value;
    const duration = 600;
    const startTime = performance.now();
    let rafId;

    function step(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      el.textContent = Math.round(start + (end - start) * eased).toLocaleString();
      if (progress < 1) {
        rafId = requestAnimationFrame(step);
      } else {
        prevRef.current = end; // Remember for next animation start point
      }
    }

    rafId = requestAnimationFrame(step);
    // Cleanup: cancel animation if component unmounts mid-animation
    return () => cancelAnimationFrame(rafId);
  }, [value]);

  return (
    <div className={styles.statCard}>
      <span className={styles.statValue} ref={elRef} aria-label={`${value} ${label}`}>
        {value.toLocaleString()}
      </span>
      <span className={styles.statLabel}>{label}</span>
    </div>
  );
});

/**
 * StatsBar — displays summary statistics.
 * React.memo: only re-renders when filteredCerts or totalCerts changes.
 *
 * @param {{ filteredCerts: Array, totalCerts: number }} props
 */
const StatsBar = memo(function StatsBar({ filteredCerts, totalCerts }) {
  const stats = getStats(filteredCerts);

  return (
    <div className={styles.statsBar} role="region" aria-label="Certification statistics">
      <div className={styles.inner}>
        <AnimatedCount value={stats.total} label="Certifications" />
        <AnimatedCount value={stats.hours} label="Verified Hours" />
        <AnimatedCount value={stats.legacy} label="Legacy Certs" />
        <AnimatedCount value={stats.newCurriculum} label="New Curriculum" />
      </div>
    </div>
  );
});

export default StatsBar;

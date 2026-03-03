import { useEffect, useMemo, useState } from "react";
import styles from "./ProductivityScore.module.css";

function useReducedMotion() {
  const [reduced, setReduced] = useState(() =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  );

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handleChange = () => setReduced(media.matches);
    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, []);

  return reduced;
}

function getTrendArrow(trend) {
  if (trend === "up") {
    return "↑";
  }
  if (trend === "down") {
    return "↓";
  }
  return "→";
}

function formatPeakWindow(peakHours = []) {
  if (!peakHours.length) {
    return "N/A";
  }
  const first = String(peakHours[0]).padStart(2, "0");
  const second = String((peakHours[0] + 1) % 24).padStart(2, "0");
  return `${first}:00-${second}:00`;
}

function ProductivityScore({ score = 0, trend = "stable", streak = 0, peakHours = [] }) {
  const reducedMotion = useReducedMotion();
  const safeScore = Math.max(0, Math.min(100, Number(score)));
  const [animatedScore, setAnimatedScore] = useState(reducedMotion ? safeScore : 0);

  useEffect(() => {
    if (reducedMotion) {
      setAnimatedScore(safeScore);
      return undefined;
    }

    let rafId = 0;
    const duration = 850;
    const startTime = performance.now();

    const animate = (time) => {
      const progress = Math.min(1, (time - startTime) / duration);
      setAnimatedScore(Math.round(progress * safeScore));
      if (progress < 1) {
        rafId = requestAnimationFrame(animate);
      }
    };

    rafId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafId);
  }, [reducedMotion, safeScore]);

  const geometry = useMemo(() => {
    const radius = 56;
    const circumference = 2 * Math.PI * radius;
    const progress = animatedScore / 100;
    return {
      radius,
      circumference,
      offset: circumference * (1 - progress),
    };
  }, [animatedScore]);

  return (
    <div className={styles.wrapper}>
      <svg viewBox="0 0 180 180" className={styles.svg} role="img" aria-label={`Productivity score ${animatedScore} out of 100.`}>
        <defs>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#94a3b8" />
            <stop offset="100%" stopColor="var(--color-accent)" />
          </linearGradient>
        </defs>
        <circle cx="90" cy="90" r={geometry.radius} className={styles.track} />
        <circle
          cx="90"
          cy="90"
          r={geometry.radius}
          className={styles.progress}
          strokeDasharray={geometry.circumference}
          strokeDashoffset={geometry.offset}
        />
        <text x="90" y="88" textAnchor="middle" className={styles.value}>
          {animatedScore}
        </text>
        <text x="90" y="107" textAnchor="middle" className={styles.max}>
          /100
        </text>
      </svg>

      <div className={styles.meta}>
        <p>
          Trend: <strong>{getTrendArrow(trend)}</strong>
        </p>
        <p>
          {streak}-day streak
        </p>
        <p>
          Peak: <span className={styles.mono}>{formatPeakWindow(peakHours)}</span>
        </p>
      </div>
    </div>
  );
}

export default ProductivityScore;

import { useMemo } from "react";
import styles from "./StatusBreakdown.module.css";

const COLORS = {
  todo: "#60a5fa",
  in_progress: "#f59e0b",
  done: "#22c55e",
  archived: "#94a3b8",
};

function StatusBreakdown({ data = {} }) {
  const segments = useMemo(() => {
    const ordered = ["todo", "in_progress", "done", "archived"].map((key) => ({
      key,
      value: Number(data[key] ?? 0),
    }));
    const total = ordered.reduce((sum, segment) => sum + segment.value, 0);
    const circumference = 2 * Math.PI * 58;
    let offset = 0;
    const withGeometry = ordered.map((segment) => {
      const portion = total > 0 ? segment.value / total : 0;
      const dash = portion * circumference;
      const current = {
        ...segment,
        dash,
        offset,
      };
      offset += dash;
      return current;
    });
    return { total, circumference, items: withGeometry };
  }, [data]);

  if (segments.total === 0) {
    return <p className={styles.empty}>No status data available.</p>;
  }

  const doneCount = segments.items.find((item) => item.key === "done")?.value ?? 0;
  const completionRate = Math.round((doneCount / segments.total) * 100);

  return (
    <div className={styles.wrapper}>
      <svg viewBox="0 0 200 200" className={styles.svg} role="img" aria-label="Task status breakdown donut chart.">
        <circle cx="100" cy="100" r="58" className={styles.track} />
        <g transform="rotate(-90 100 100)">
          {segments.items.map((segment) => (
            <circle
              key={segment.key}
              className={styles.segment}
              cx="100"
              cy="100"
              r="58"
              stroke={COLORS[segment.key]}
              strokeDasharray={`${segment.dash} ${segments.circumference - segment.dash}`}
              strokeDashoffset={-segment.offset}
            />
          ))}
        </g>
        <text x="100" y="96" textAnchor="middle" className={styles.totalLabel}>
          {segments.total}
        </text>
        <text x="100" y="116" textAnchor="middle" className={styles.subLabel}>
          {completionRate}% done
        </text>
      </svg>

      <ul className={styles.legend}>
        {segments.items.map((segment) => (
          <li key={segment.key}>
            <span className={styles.swatch} style={{ background: COLORS[segment.key] }} />
            <span>{segment.key.replace("_", " ")}</span>
            <strong>{segment.value}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default StatusBreakdown;

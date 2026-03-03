import { useMemo, useState } from "react";
import styles from "./Heatmap.module.css";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function getCountValue(cell) {
  if (!cell) {
    return 0;
  }
  return Number(cell.count ?? 0);
}

function Heatmap({ data = [] }) {
  const [hoveredCell, setHoveredCell] = useState(null);

  const matrix = useMemo(() => {
    const cells = Array.from({ length: 7 * 24 }, (_, index) => ({
      day: Math.floor(index / 24),
      hour: index % 24,
      count: 0,
    }));

    data.forEach((entry) => {
      const day = Number(entry.day_of_week ?? entry.day ?? 0);
      const hour = Number(entry.hour_of_day ?? entry.hour ?? 0);
      if (day >= 0 && day < 7 && hour >= 0 && hour < 24) {
        cells[day * 24 + hour].count = Number(entry.count ?? 0);
      }
    });

    const maxCount = Math.max(0, ...cells.map((cell) => cell.count));
    return { cells, maxCount };
  }, [data]);

  if (!data.length) {
    return <p className={styles.empty}>No activity data available.</p>;
  }

  const cellSize = 14;
  const gap = 3;
  const leftPadding = 40;
  const topPadding = 20;
  const width = leftPadding + 24 * (cellSize + gap) + 18;
  const height = topPadding + 7 * (cellSize + gap) + 20;

  return (
    <div className={styles.wrapper}>
      <svg
        className={styles.svg}
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Activity heatmap grouped by day of week and hour of day."
      >
        {DAYS.map((day, index) => (
          <text key={day} x={4} y={topPadding + index * (cellSize + gap) + 11} className={styles.dayLabel}>
            {day}
          </text>
        ))}

        {Array.from({ length: 24 }, (_, hour) => (
          <text
            key={`hour-${hour}`}
            x={leftPadding + hour * (cellSize + gap)}
            y={12}
            className={styles.hourLabel}
            style={{ visibility: hour % 4 === 0 ? "visible" : "hidden" }}
          >
            {hour}
          </text>
        ))}

        {matrix.cells.map((cell) => {
          const x = leftPadding + cell.hour * (cellSize + gap);
          const y = topPadding + cell.day * (cellSize + gap);
          const normalized = matrix.maxCount > 0 ? cell.count / matrix.maxCount : 0;
          const opacity = 0.18 + normalized * 0.82;
          const fill = cell.count === 0 ? "var(--color-surface-2)" : "var(--color-accent)";

          return (
            <rect
              key={`${cell.day}-${cell.hour}`}
              x={x}
              y={y}
              width={cellSize}
              height={cellSize}
              rx="2"
              fill={fill}
              fillOpacity={cell.count === 0 ? 1 : opacity}
              stroke="var(--color-border)"
              onMouseEnter={() => setHoveredCell(cell)}
              onMouseLeave={() => setHoveredCell(null)}
            />
          );
        })}
      </svg>

      {hoveredCell && (
        <div className={styles.tooltip}>
          {DAYS[hoveredCell.day]} {String(hoveredCell.hour).padStart(2, "0")}:00 - {hoveredCell.count} events
        </div>
      )}
    </div>
  );
}

export default Heatmap;

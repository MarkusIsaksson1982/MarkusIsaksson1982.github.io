import { useMemo, useState } from "react";
import styles from "./TrendChart.module.css";

const VIEWBOX_WIDTH = 640;
const VIEWBOX_HEIGHT = 280;
const PADDING = { top: 24, right: 24, bottom: 34, left: 42 };

function createLinePath(points) {
  if (!points.length) {
    return "";
  }
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
}

function formatLabel(dateText) {
  return new Date(dateText).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

function TrendChart({ data = [], movingAvg = [] }) {
  const [hoverIndex, setHoverIndex] = useState(null);

  const chart = useMemo(() => {
    if (!data.length) {
      return null;
    }

    const innerWidth = VIEWBOX_WIDTH - PADDING.left - PADDING.right;
    const innerHeight = VIEWBOX_HEIGHT - PADDING.top - PADDING.bottom;
    const maxY = Math.max(
      1,
      ...data.map((item) => item.created ?? 0),
      ...data.map((item) => item.completed ?? 0),
      ...movingAvg.map((item) => item.value ?? 0),
    );

    const toPoint = (index, value) => {
      const x =
        PADDING.left +
        (data.length <= 1 ? innerWidth / 2 : (index / (data.length - 1)) * innerWidth);
      const y = PADDING.top + innerHeight - (value / maxY) * innerHeight;
      return { x, y };
    };

    const createdPoints = data.map((item, index) => toPoint(index, item.created ?? 0));
    const completedPoints = data.map((item, index) => toPoint(index, item.completed ?? 0));
    const movingAveragePoints = movingAvg.map((item, index) => toPoint(index, item.value ?? 0));

    return {
      maxY,
      createdPoints,
      completedPoints,
      movingAveragePoints,
      createdPath: createLinePath(createdPoints),
      completedPath: createLinePath(completedPoints),
      movingAvgPath: createLinePath(movingAveragePoints),
    };
  }, [data, movingAvg]);

  if (!chart) {
    return <p className={styles.empty}>No trend data available.</p>;
  }

  const yTicks = Array.from({ length: 5 }, (_, index) => Math.round((chart.maxY * index) / 4));

  return (
    <div className={styles.wrapper}>
      <svg
        className={styles.svg}
        viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
        role="img"
        aria-label="Trend chart showing tasks created and completed by day."
      >
        <g>
          {yTicks.map((tick) => {
            const y =
              PADDING.top +
              (VIEWBOX_HEIGHT - PADDING.top - PADDING.bottom) -
              (tick / chart.maxY) * (VIEWBOX_HEIGHT - PADDING.top - PADDING.bottom);
            return (
              <g key={tick}>
                <line className={styles.gridLine} x1={PADDING.left} y1={y} x2={VIEWBOX_WIDTH - PADDING.right} y2={y} />
                <text className={styles.axisLabel} x={8} y={y + 4}>
                  {tick}
                </text>
              </g>
            );
          })}
        </g>

        <path className={`${styles.line} ${styles.created}`} d={chart.createdPath} />
        <path className={`${styles.line} ${styles.completed}`} d={chart.completedPath} />
        {movingAvg.length > 0 && <path className={`${styles.line} ${styles.movingAvg}`} d={chart.movingAvgPath} />}

        {chart.completedPoints.map((point, index) => (
          <circle
            key={`${data[index].date}-pt`}
            className={styles.point}
            cx={point.x}
            cy={point.y}
            r={4}
            onMouseEnter={() => setHoverIndex(index)}
            onFocus={() => setHoverIndex(index)}
            onMouseLeave={() => setHoverIndex(null)}
          />
        ))}

        <g>
          <text className={styles.axisLabel} x={PADDING.left} y={VIEWBOX_HEIGHT - 8}>
            {formatLabel(data[0].date)}
          </text>
          <text className={styles.axisLabel} x={VIEWBOX_WIDTH - PADDING.right - 52} y={VIEWBOX_HEIGHT - 8}>
            {formatLabel(data[data.length - 1].date)}
          </text>
        </g>
      </svg>

      {hoverIndex !== null && data[hoverIndex] && (
        <div className={styles.tooltip} role="status" aria-live="polite">
          <p>{formatLabel(data[hoverIndex].date)}</p>
          <p>Created: {data[hoverIndex].created}</p>
          <p>Completed: {data[hoverIndex].completed}</p>
        </div>
      )}
    </div>
  );
}

export default TrendChart;

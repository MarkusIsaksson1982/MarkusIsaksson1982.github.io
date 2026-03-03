import { useState } from "react";
import { useAnalytics } from "../hooks/useAnalytics.js";
import TrendChart from "../components/charts/TrendChart.jsx";
import StatusBreakdown from "../components/charts/StatusBreakdown.jsx";
import Heatmap from "../components/charts/Heatmap.jsx";
import ProductivityScore from "../components/charts/ProductivityScore.jsx";
import styles from "./AnalyticsPage.module.css";

const PERIOD_OPTIONS = [
  { label: "7d", value: "7d" },
  { label: "30d", value: "30d" },
  { label: "90d", value: "90d" },
];

function formatPercent(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}

function AnalyticsPage() {
  const [period, setPeriod] = useState("30d");
  const { summary, trends, heatmap, productivity, loading, error, refresh } = useAnalytics(period);

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <div>
          <h2>Analytics Dashboard</h2>
          <p>Explore throughput, completion velocity, and activity patterns.</p>
        </div>
        <div className={styles.controls}>
          <div className={styles.periodGroup} role="group" aria-label="Analytics period">
            {PERIOD_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={period === option.value ? styles.periodActive : styles.periodButton}
                onClick={() => setPeriod(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
          <button className={styles.refreshButton} type="button" onClick={refresh}>
            Refresh
          </button>
        </div>
      </header>

      {error && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}

      <section className={styles.summaryGrid} aria-label="Summary metrics">
        <article className={`card ${styles.summaryCard}`}>
          <h3>Total Tasks</h3>
          <p>{summary?.total ?? 0}</p>
        </article>
        <article className={`card ${styles.summaryCard}`}>
          <h3>Completion Rate</h3>
          <p>{formatPercent(summary?.completion_rate)}</p>
        </article>
        <article className={`card ${styles.summaryCard}`}>
          <h3>Avg Completion Time</h3>
          <p>{summary?.avg_completion_time_hours ?? 0}h</p>
        </article>
        <article className={`card ${styles.summaryCard}`}>
          <h3>Streak</h3>
          <p>{productivity?.streak ?? 0} days</p>
        </article>
      </section>

      {loading && <p className={styles.loading}>Loading analytics...</p>}

      <section className={styles.chartGrid}>
        <article className={`card ${styles.chartCard}`}>
          <header>
            <h3>Created vs Completed</h3>
          </header>
          <TrendChart data={trends?.data ?? []} movingAvg={trends?.moving_avg ?? []} />
        </article>

        <article className={`card ${styles.chartCard}`}>
          <header>
            <h3>Status Breakdown</h3>
          </header>
          <StatusBreakdown data={summary?.by_status ?? {}} />
        </article>

        <article className={`card ${styles.chartCard}`}>
          <header>
            <h3>Activity Heatmap</h3>
          </header>
          <Heatmap data={heatmap?.data ?? []} />
        </article>

        <article className={`card ${styles.chartCard}`}>
          <header>
            <h3>Productivity Score</h3>
          </header>
          <ProductivityScore
            score={productivity?.score ?? 0}
            trend={productivity?.trend ?? "stable"}
            streak={productivity?.streak ?? 0}
            peakHours={productivity?.peak_hours ?? []}
          />
          {productivity?.insights?.length > 0 && (
            <ul className={styles.insights}>
              {productivity.insights.map((insight) => (
                <li key={insight}>{insight}</li>
              ))}
            </ul>
          )}
        </article>
      </section>
    </section>
  );
}

export default AnalyticsPage;

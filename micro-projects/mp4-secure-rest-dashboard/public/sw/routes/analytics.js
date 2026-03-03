import { successResponse } from "../utils/http.js";

const PERIOD_MAP = {
  "7d": 7,
  "30d": 30,
  "90d": 90,
};

const DAY_MS = 24 * 60 * 60 * 1000;

function resolvePeriod(value, fallback = 30) {
  return PERIOD_MAP[value] ?? fallback;
}

function startOfDay(timestamp) {
  const date = new Date(timestamp);
  date.setHours(0, 0, 0, 0);
  return date.getTime();
}

function formatDateKey(timestamp) {
  return new Date(timestamp).toISOString().slice(0, 10);
}

function getActiveTasks(tasks) {
  return tasks.filter((task) => !task.deleted_at);
}

function average(values) {
  if (!values.length) {
    return 0;
  }
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function rollingAverage(series, windowSize) {
  return series.map((_, index) => {
    const start = Math.max(0, index - windowSize + 1);
    const slice = series.slice(start, index + 1);
    return average(slice);
  });
}

function calculateStreak(tasks) {
  const completedByDay = new Set(
    tasks
      .filter((task) => task.completed_at)
      .map((task) => formatDateKey(startOfDay(task.completed_at))),
  );

  let streak = 0;
  for (let i = 0; i < 365; i += 1) {
    const day = new Date();
    day.setHours(0, 0, 0, 0);
    day.setDate(day.getDate() - i);
    const key = day.toISOString().slice(0, 10);
    if (completedByDay.has(key)) {
      streak += 1;
    } else {
      break;
    }
  }

  return streak;
}

function calculatePeakHours(tasks) {
  const buckets = new Array(24).fill(0);
  tasks.forEach((task) => {
    const timestamp = task.completed_at ?? task.updated_at ?? task.created_at;
    const hour = new Date(timestamp).getHours();
    buckets[hour] += 1;
  });

  const max = Math.max(...buckets);
  const peakHours = [];
  buckets.forEach((count, hour) => {
    if (count === max && count > 0) {
      peakHours.push(hour);
    }
  });
  return peakHours;
}

function buildInsights({ completionRate, overdueCount, doneLast7Days, streak, peakHours }) {
  const insights = [];

  if (completionRate >= 0.7) {
    insights.push("Completion rate is strong this period.");
  } else if (completionRate < 0.4) {
    insights.push("Completion rate is low; consider reducing active work-in-progress.");
  }

  if (overdueCount > 0) {
    insights.push(`${overdueCount} overdue task(s) need attention.`);
  } else {
    insights.push("No overdue tasks detected.");
  }

  if (doneLast7Days >= 7) {
    insights.push("Consistent weekly delivery trend.");
  } else if (doneLast7Days <= 2) {
    insights.push("Low completion volume this week.");
  }

  if (streak >= 5) {
    insights.push(`Great momentum: ${streak}-day completion streak.`);
  }

  if (peakHours.length > 0) {
    const labels = peakHours.slice(0, 3).map((hour) => `${String(hour).padStart(2, "0")}:00`);
    insights.push(`Peak productivity window: ${labels.join(", ")}.`);
  }

  return insights.slice(0, 5);
}

export function registerAnalyticsRoutes(router, { db, requireAuth, apiRateLimit }) {
  router.get("/api/analytics/summary", requireAuth, apiRateLimit("analytics:summary"), async (req) => {
    const tasks = getActiveTasks(
      await db.getAll("tasks", {
        index: "user_id",
        range: IDBKeyRange.only(req.user.id),
      }),
    );

    const byStatus = {};
    const byPriority = {};
    const byCategory = {};

    tasks.forEach((task) => {
      byStatus[task.status] = (byStatus[task.status] ?? 0) + 1;
      byPriority[task.priority] = (byPriority[task.priority] ?? 0) + 1;
      byCategory[task.category] = (byCategory[task.category] ?? 0) + 1;
    });

    const completed = tasks.filter((task) => task.status === "done");
    const completionRate = tasks.length ? completed.length / tasks.length : 0;
    const completionDurations = completed
      .filter((task) => task.completed_at && task.created_at)
      .map((task) => task.completed_at - task.created_at);
    const avgCompletionTimeHours = average(completionDurations) / (1000 * 60 * 60);

    return successResponse({
      total: tasks.length,
      by_status: byStatus,
      by_priority: byPriority,
      by_category: byCategory,
      completion_rate: Number(completionRate.toFixed(4)),
      avg_completion_time_hours: Number(avgCompletionTimeHours.toFixed(2)),
    });
  });

  router.get("/api/analytics/trends", requireAuth, apiRateLimit("analytics:trends"), async (req) => {
    const periodDays = resolvePeriod(req.query.period, 30);
    const now = Date.now();
    const start = startOfDay(now - (periodDays - 1) * DAY_MS);

    const tasks = getActiveTasks(
      await db.getAll("tasks", {
        index: "user_id",
        range: IDBKeyRange.only(req.user.id),
      }),
    );

    const buckets = Array.from({ length: periodDays }, (_, offset) => {
      const dayTimestamp = start + offset * DAY_MS;
      return {
        date: formatDateKey(dayTimestamp),
        created: 0,
        completed: 0,
      };
    });
    const lookup = new Map(buckets.map((entry, index) => [entry.date, index]));

    tasks.forEach((task) => {
      const createdKey = formatDateKey(startOfDay(task.created_at));
      const createdIndex = lookup.get(createdKey);
      if (createdIndex !== undefined) {
        buckets[createdIndex].created += 1;
      }
      if (task.completed_at) {
        const completedKey = formatDateKey(startOfDay(task.completed_at));
        const completedIndex = lookup.get(completedKey);
        if (completedIndex !== undefined) {
          buckets[completedIndex].completed += 1;
        }
      }
    });

    const movingAvg = rollingAverage(
      buckets.map((entry) => entry.completed),
      7,
    ).map((value, index) => ({
      date: buckets[index].date,
      value: Number(value.toFixed(2)),
    }));

    const data = buckets.map((entry, index) => ({
      ...entry,
      rolling_avg: movingAvg[index].value,
    }));

    return successResponse({
      data,
      moving_avg: movingAvg,
      period: `${periodDays}d`,
    });
  });

  router.get("/api/analytics/heatmap", requireAuth, apiRateLimit("analytics:heatmap"), async (req) => {
    const periodDays = resolvePeriod(req.query.period, 30);
    const now = Date.now();
    const start = now - periodDays * DAY_MS;

    const logs = await db.getAll("audit_log", {
      index: "user_timestamp",
      range: IDBKeyRange.bound([req.user.id, start], [req.user.id, now]),
    });

    const buckets = Array.from({ length: 7 * 24 }, (_, index) => ({
      day_of_week: Math.floor(index / 24),
      hour_of_day: index % 24,
      count: 0,
    }));

    logs.forEach((log) => {
      const date = new Date(log.timestamp);
      const isoDay = (date.getDay() + 6) % 7;
      const hour = date.getHours();
      const bucketIndex = isoDay * 24 + hour;
      buckets[bucketIndex].count += 1;
    });

    return successResponse({
      data: buckets,
      period: `${periodDays}d`,
    });
  });

  router.get(
    "/api/analytics/productivity",
    requireAuth,
    apiRateLimit("analytics:productivity"),
    async (req) => {
      const now = Date.now();
      const tasks = getActiveTasks(
        await db.getAll("tasks", {
          index: "user_id",
          range: IDBKeyRange.only(req.user.id),
        }),
      );

      const completed = tasks.filter((task) => task.status === "done");
      const doneLast7Days = completed.filter((task) => task.completed_at && task.completed_at >= now - 7 * DAY_MS).length;
      const completionRate = tasks.length ? completed.length / tasks.length : 0;
      const overdueCount = tasks.filter((task) => task.status !== "done" && task.due_date && task.due_date < now).length;
      const streak = calculateStreak(tasks);
      const peakHours = calculatePeakHours(completed.length ? completed : tasks);

      const completionComponent = Math.min(55, completionRate * 55);
      const velocityComponent = Math.min(25, doneLast7Days * 3.5);
      const overduePenalty = Math.min(20, overdueCount * 2.5);
      const score = Math.max(0, Math.min(100, Math.round(completionComponent + velocityComponent - overduePenalty + 20)));

      const insights = buildInsights({
        completionRate,
        overdueCount,
        doneLast7Days,
        streak,
        peakHours,
      });

      return successResponse({
        score,
        streak,
        peak_hours: peakHours,
        trend: doneLast7Days >= 5 ? "up" : doneLast7Days <= 2 ? "down" : "stable",
        insights,
        completion_rate: Number(completionRate.toFixed(4)),
        weekly_completed: doneLast7Days,
        overdue: overdueCount,
      });
    },
  );
}

import { generateSalt, hashPassword, generateUUID } from "../utils/crypto.js";

const DAY_MS = 24 * 60 * 60 * 1000;
const CATEGORY_TITLES = {
  development: [
    "Implement user authentication flow",
    "Refactor API request handling",
    "Add pagination to task endpoint",
    "Improve error boundary behavior",
    "Optimize route matching performance",
    "Build reusable data fetch hook",
    "Add optimistic task updates",
    "Harden task mutation validation",
  ],
  design: [
    "Create dashboard card wireframes",
    "Update dark mode token mapping",
    "Polish mobile navigation spacing",
    "Refine chart legend readability",
    "Design empty state illustrations",
    "Improve form focus styles",
  ],
  documentation: [
    "Write API endpoint documentation",
    "Document service worker lifecycle",
    "Update README setup section",
    "Add architecture decision record",
    "Document analytics scoring formula",
  ],
  testing: [
    "Write auth middleware test cases",
    "Validate route ownership checks",
    "Test analytics aggregation output",
    "Verify rate limiter edge cases",
    "Run accessibility smoke checks",
  ],
  deployment: [
    "Configure GitHub Pages build step",
    "Set cache headers for static assets",
    "Prepare release checklist",
    "Validate offline fallback behavior",
    "Test hashed assets on deploy preview",
  ],
  research: [
    "Compare IndexedDB query strategies",
    "Evaluate JWT expiry tradeoffs",
    "Review token bucket tuning options",
    "Investigate chart interaction patterns",
    "Assess service worker update prompts",
  ],
};

const STATUS_WEIGHTS = [
  { value: "todo", weight: 20 },
  { value: "in_progress", weight: 15 },
  { value: "done", weight: 50 },
  { value: "archived", weight: 15 },
];

const PRIORITY_WEIGHTS = [
  { value: "medium", weight: 40 },
  { value: "high", weight: 25 },
  { value: "low", weight: 20 },
  { value: "critical", weight: 15 },
];

const CATEGORIES = Object.keys(CATEGORY_TITLES);

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function chooseWeighted(entries) {
  const total = entries.reduce((sum, item) => sum + item.weight, 0);
  let cursor = Math.random() * total;
  for (const item of entries) {
    cursor -= item.weight;
    if (cursor <= 0) {
      return item.value;
    }
  }
  return entries[entries.length - 1].value;
}

function pickRandom(items) {
  return items[randomInt(0, items.length - 1)];
}

function randomRecentTimestamp(daysBack) {
  const now = Date.now();
  const weekdayBias = Math.random() < 0.75;
  for (let i = 0; i < 20; i += 1) {
    const candidate = now - randomInt(0, daysBack * DAY_MS);
    const day = new Date(candidate).getDay();
    const isWeekday = day >= 1 && day <= 5;
    if (!weekdayBias || isWeekday) {
      return candidate;
    }
  }
  return now - randomInt(0, daysBack * DAY_MS);
}

function buildDescription(category, status) {
  const phrases = {
    development: "Coordinate with API and frontend contracts before merge.",
    design: "Validate visual consistency against inherited MP tokens.",
    documentation: "Include concise examples and update edge-case notes.",
    testing: "Cover expected behavior plus one regression case.",
    deployment: "Confirm GitHub Pages behavior and cache busting.",
    research: "Summarize tradeoffs and proposed implementation path.",
  };

  return `${phrases[category]} Current status: ${status.replace("_", " ")}.`;
}

function buildDueDate(status, createdAt) {
  const hasDueDate = Math.random() < 0.6;
  if (!hasDueDate) {
    return null;
  }

  if (status === "todo" || status === "in_progress") {
    const overdue = Math.random() < 0.35;
    if (overdue) {
      return createdAt + randomInt(1, 12) * DAY_MS;
    }
    return Date.now() + randomInt(1, 21) * DAY_MS;
  }

  return createdAt + randomInt(2, 20) * DAY_MS;
}

function computeCompletionTimestamp(status, createdAt) {
  if (status !== "done") {
    return null;
  }
  const completedAt = createdAt + randomInt(1, 14) * DAY_MS;
  return Math.min(completedAt, Date.now() - randomInt(0, 2) * 60 * 60 * 1000);
}

function buildTaskTimestamp(status) {
  if (status === "todo" || status === "in_progress") {
    return randomRecentTimestamp(14);
  }
  return randomRecentTimestamp(90);
}

function createTaskRecord(userId) {
  const status = chooseWeighted(STATUS_WEIGHTS);
  const priority = chooseWeighted(PRIORITY_WEIGHTS);
  const category = pickRandom(CATEGORIES);
  const createdAt = buildTaskTimestamp(status);
  const completedAt = computeCompletionTimestamp(status, createdAt);
  const updatedAt = completedAt ?? Math.max(createdAt, createdAt + randomInt(2, 72) * 60 * 60 * 1000);
  const title = pickRandom(CATEGORY_TITLES[category]);

  return {
    id: generateUUID(),
    user_id: userId,
    title,
    description: buildDescription(category, status),
    status,
    priority,
    category,
    due_date: buildDueDate(status, createdAt),
    created_at: createdAt,
    updated_at: Math.min(updatedAt, Date.now()),
    completed_at: completedAt,
  };
}

function createAuditLogsForTask(task) {
  const logs = [
    {
      id: generateUUID(),
      user_id: task.user_id,
      action: "task.create",
      resource_id: task.id,
      detail: JSON.stringify({ status: task.status, priority: task.priority }),
      timestamp: task.created_at,
    },
  ];

  if (task.status === "done" && task.completed_at) {
    logs.push({
      id: generateUUID(),
      user_id: task.user_id,
      action: "task.complete",
      resource_id: task.id,
      detail: JSON.stringify({ completed_at: task.completed_at }),
      timestamp: task.completed_at,
    });
  }

  if (task.status === "archived") {
    logs.push({
      id: generateUUID(),
      user_id: task.user_id,
      action: "task.archive",
      resource_id: task.id,
      detail: JSON.stringify({ archived: true }),
      timestamp: task.updated_at,
    });
  }

  return logs;
}

export async function seedDatabase(db) {
  const existingUsers = await db.getAll("users");
  if (existingUsers.length > 0) {
    return {
      userCount: existingUsers.length,
      taskCount: (await db.getAll("tasks")).length,
      logCount: (await db.getAll("audit_log")).length,
      seeded: false,
    };
  }

  const createdAt = Date.now() - 120 * DAY_MS;
  const salt = generateSalt();
  const pwHash = await hashPassword("demo1234", salt);
  const demoUser = {
    id: generateUUID(),
    username: "demo",
    pw_hash: pwHash,
    pw_salt: salt,
    created_at: createdAt,
    last_login: null,
  };

  const taskCount = randomInt(40, 50);
  const tasks = Array.from({ length: taskCount }, () => createTaskRecord(demoUser.id));
  const auditLogs = [
    {
      id: generateUUID(),
      user_id: demoUser.id,
      action: "auth.register",
      resource_id: demoUser.id,
      detail: JSON.stringify({ username: demoUser.username }),
      timestamp: createdAt,
    },
  ];

  tasks.forEach((task) => {
    auditLogs.push(...createAuditLogsForTask(task));
  });

  await db.transaction(["users", "tasks", "audit_log"], "readwrite", (stores) => {
    stores.users.put(demoUser);
    tasks.forEach((task) => stores.tasks.put(task));
    auditLogs.forEach((log) => stores.audit_log.put(log));
  });

  return {
    userCount: 1,
    taskCount: tasks.length,
    logCount: auditLogs.length,
    seeded: true,
  };
}

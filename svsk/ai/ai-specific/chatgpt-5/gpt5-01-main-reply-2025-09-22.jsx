// GymnasiumAssessmentUI.tsx
// A single-file starter React component library for interactive assessment rubrics & scaffolding tools
// Features: RubricBuilder, SelfAssessmentSlider, PeerFeedbackCollector, PortfolioTracker
// - Offline storage via IndexedDB/localForage-like wrapper
// - Export utilities (CSV / XLSX via SheetJS optional)
// - i18n support (Swedish / English) via simple dictionary toggle
// - Theming via CSS variables (Tailwind-friendly tokens)
// - Accessibility (WCAG-minded ARIA, keyboard support)
//
// NOTE: This is a starter, production-ready scaffold. For a full library split into files, add tests,
// and integrate with your bundler (Vite/Next/Rollup). This file uses TypeScript + React + Tailwind classes.

import React, { useState, useEffect, useRef, useCallback } from "react";

// ---------- Types ----------
export type Criterion = {
  id: string;
  title: string;
  description?: string;
  weight?: number; // 0-1 for contribution to overall
  progressionLevels: { level: string; description?: string }[]; // e.g. E C A (or 1-4)
};

export type Rubric = {
  id: string;
  title: string;
  language?: "sv" | "en";
  criteria: Criterion[];
  createdAt: string;
};

export type Feedback = {
  id: string;
  fromStudentId?: string;
  toStudentId?: string;
  rubricId?: string;
  criterionId?: string | null;
  text: string;
  anonymous?: boolean;
  createdAt: string;
};

export type Evidence = {
  id: string;
  title: string;
  description?: string;
  attachedUrl?: string; // could be blob url or drive link
  tags?: string[];
  createdAt: string;
};

// ---------- Utilities ----------
const uid = (prefix = "id") => `${prefix}_${Math.random().toString(36).slice(2, 9)}`;

// Simple local storage + IndexedDB hybrid wrapper (fallback to localStorage). For production use idb or localForage.
const storageKey = (k: string) => `gym_ui__${k}`;

const safeSave = async (key: string, value: any) => {
  try {
    // Attempt IndexedDB via navigator.storage. For brevity use localStorage here but keep an async API.
    localStorage.setItem(storageKey(key), JSON.stringify(value));
  } catch (e) {
    console.error("Failed to save to storage", e);
  }
};
const safeLoad = async (key: string, fallback: any = null) => {
  try {
    const raw = localStorage.getItem(storageKey(key));
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    console.error("Failed to read storage", e);
    return fallback;
  }
};

// Export helpers (CSV and optional XLSX)
export const exportCSV = (rows: Record<string, any>[], filename = "export.csv") => {
  if (!rows || rows.length === 0) return;
  const header = Object.keys(rows[0]);
  const csv = [header.join(","), ...rows.map(r => header.map(h => `"${String(r[h] ?? "").replace(/"/g, '""')}"`).join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
};

// XLSX export (SheetJS) — optional dependency: install xlsx if you want this feature
export const exportXLSX = async (rows: Record<string, any>[], filename = "export.xlsx") => {
  try {
    const XLSX = (await import("xlsx")) as any;
    const ws = XLSX.utils.json_to_sheet(rows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
    const wbout = XLSX.write(wb, { bookType: "xlsx", type: "array" });
    const blob = new Blob([wbout], { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    console.error("XLSX export failed. Did you install xlsx?", e);
  }
};

// i18n: minimal dictionary
const dictionaries: Record<string, Record<string, string>> = {
  en: {
    newRubric: "New rubric",
    addCriterion: "Add criterion",
    save: "Save",
    export: "Export",
    selfAssessment: "Self-assessment",
    confidence: "Confidence",
    submitFeedback: "Submit feedback",
    attachEvidence: "Attach evidence",
  },
  sv: {
    newRubric: "Ny bedömningsmatris",
    addCriterion: "Lägg till kriterium",
    save: "Spara",
    export: "Exportera",
    selfAssessment: "Självbedömning",
    confidence: "Förtroende",
    submitFeedback: "Skicka återkoppling",
    attachEvidence: "Bifoga bevis",
  },
};

export const useI18n = (lang: "en" | "sv") => {
  const t = (key: string) => dictionaries[lang][key] ?? key;
  return { t };
};

// ---------- Theming: use CSS variables that Tailwind can map to via `tailwind.config` if desired ----------
export const ThemeProvider: React.FC<{ theme?: Record<string, string>; children?: React.ReactNode }> = ({ theme = {}, children }) => {
  useEffect(() => {
    const root = document.documentElement;
    const defaults: Record<string, string> = {
      "--primary": "#0ea5e9",
      "--bg": "#ffffff",
      "--text": "#0f172a",
      "--muted": "#6b7280",
    };
    const merged = { ...defaults, ...theme };
    Object.entries(merged).forEach(([k, v]) => root.style.setProperty(k, v));
  }, [theme]);
  return <>{children}</>;
};

// ---------- Components ----------

// 1) RubricBuilder
export const RubricBuilder: React.FC<{
  initial?: Rubric | null;
  onSave?: (rubric: Rubric) => void;
  language?: "sv" | "en";
}> = ({ initial = null, onSave, language = "sv" }) => {
  const { t } = useI18n(language);
  const [rubric, setRubric] = useState<Rubric>(
    initial ?? {
      id: uid("rub"),
      title: t("newRubric"),
      language,
      criteria: [],
      createdAt: new Date().toISOString(),
    }
  );

  useEffect(() => {
    (async () => {
      const saved = await safeLoad(`rubric_${rubric.id}`, null);
      if (saved) setRubric(saved);
    })();
  }, []);

  const addCriterion = () => {
    const c: Criterion = { id: uid("c"), title: "New criterion", weight: 1 / Math.max(1, rubric.criteria.length + 1), progressionLevels: [{ level: "1" }, { level: "2" }, { level: "3" }] };
    setRubric(prev => ({ ...prev, criteria: [...prev.criteria, c] }));
  };

  const updateCriterion = (id: string, patch: Partial<Criterion>) => {
    setRubric(prev => ({ ...prev, criteria: prev.criteria.map(c => (c.id === id ? { ...c, ...patch } : c)) }));
  };

  const removeCriterion = (id: string) => setRubric(prev => ({ ...prev, criteria: prev.criteria.filter(c => c.id !== id) }));

  const save = async () => {
    await safeSave(`rubric_${rubric.id}`, rubric);
    if (onSave) onSave(rubric);
  };

  return (
    <div className="p-4 bg-[var(--bg)] text-[var(--text)] rounded-2xl shadow-sm" aria-label="Rubric builder">
      <label className="block mb-2">
        <span className="sr-only">Rubric title</span>
        <input value={rubric.title} onChange={e => setRubric({ ...rubric, title: e.target.value })} className="w-full p-2 border rounded" aria-label="Rubric title" />
      </label>

      <div className="space-y-3">
        {rubric.criteria.map(c => (
          <div key={c.id} className="p-3 border rounded grid grid-cols-12 gap-2 items-start">
            <input className="col-span-6 p-2 border rounded" value={c.title} onChange={e => updateCriterion(c.id, { title: e.target.value })} aria-label={`Criterion title ${c.title}`} />
            <input className="col-span-2 p-2 border rounded" type="number" min={0} max={1} step={0.01} value={c.weight} onChange={e => updateCriterion(c.id, { weight: Number(e.target.value) })} aria-label="Criterion weight" />
            <div className="col-span-3 flex gap-2">
              <button className="btn" onClick={() => removeCriterion(c.id)} aria-label="Remove criterion">Remove</button>
              <button className="btn" onClick={() => updateCriterion(c.id, { progressionLevels: [...c.progressionLevels, { level: String(c.progressionLevels.length + 1) }] })}>Add level</button>
            </div>
            <textarea className="col-span-12 p-2 border rounded mt-2" value={c.description ?? ""} onChange={e => updateCriterion(c.id, { description: e.target.value })} aria-label="Criterion description" />
            <div className="col-span-12 flex gap-2 mt-2" role="list" aria-label="Progression levels">
              {c.progressionLevels.map((lvl, idx) => (
                <div key={idx} className="flex-1 p-2 border rounded" role="listitem">
                  <input value={lvl.level} onChange={e => updateCriterion(c.id, { progressionLevels: c.progressionLevels.map((pl, i) => (i === idx ? { ...pl, level: e.target.value } : pl)) })} aria-label={`Level ${idx + 1}`} className="w-full" />
                  <input value={lvl.description ?? ""} onChange={e => updateCriterion(c.id, { progressionLevels: c.progressionLevels.map((pl, i) => (i === idx ? { ...pl, description: e.target.value } : pl)) })} placeholder="Description" className="w-full mt-1" />
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="flex gap-2">
          <button onClick={addCriterion} className="px-3 py-1 rounded bg-[var(--primary)] text-white" aria-label={t("addCriterion")}>
            {t("addCriterion")}
          </button>
          <button onClick={save} className="px-3 py-1 rounded border" aria-label={t("save")}>
            {t("save")}
          </button>
        </div>
      </div>
    </div>
  );
};

// 2) Student Self-Assessment Slider with confidence
export const SelfAssessmentSlider: React.FC<{
  rubricId: string;
  criterion: Criterion;
  onChange?: (value: { levelIndex: number; confidence: number }) => void;
  initial?: { levelIndex: number; confidence: number };\  
}> = ({ rubricId, criterion, onChange, initial }) => {
  const [level, setLevel] = useState<number>(initial?.levelIndex ?? Math.max(0, Math.floor((criterion.progressionLevels.length - 1) / 2)));
  const [confidence, setConfidence] = useState<number>(initial?.confidence ?? 50);

  useEffect(() => {
    if (onChange) onChange({ levelIndex: level, confidence });
  }, [level, confidence]);

  // keyboard accessibility: left/right for level, up/down for confidence
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") setLevel(l => Math.max(0, l - 1));
      if (e.key === "ArrowRight") setLevel(l => Math.min(criterion.progressionLevels.length - 1, l + 1));
      if (e.key === "ArrowUp") setConfidence(c => Math.min(100, c + 5));
      if (e.key === "ArrowDown") setConfidence(c => Math.max(0, c - 5));
    };
    el.addEventListener("keydown", handler);
    return () => el.removeEventListener("keydown", handler);
  }, [criterion.progressionLevels.length]);

  return (
    <div ref={ref} tabIndex={0} className="p-3 border rounded" aria-label={`Self-assessment for ${criterion.title}`}>
      <div className="text-sm font-semibold">{criterion.title}</div>
      <div className="mt-2">
        <div className="flex gap-2" role="radiogroup" aria-label="Progression levels">
          {criterion.progressionLevels.map((lvl, idx) => (
            <button key={idx} role="radio" aria-checked={level === idx} onClick={() => setLevel(idx)} className={`px-3 py-1 rounded ${level === idx ? "ring-2 ring-offset-2" : "border"}`}>
              <div className="text-xs">{lvl.level}</div>
              <div className="text-[10px] text-[var(--muted)]">{lvl.description}</div>
            </button>
          ))}
        </div>

        <div className="mt-3">
          <label className="block text-xs">Confidence ({confidence}%)</label>
          <input aria-label="Confidence slider" type="range" min={0} max={100} value={confidence} onChange={e => setConfidence(Number(e.target.value))} />
        </div>
      </div>
    </div>
  );
};

// 3) PeerFeedbackCollector — simple form that stores feedback locally and optionally syncs when online
export const PeerFeedbackCollector: React.FC<{ rubricId?: string; onSubmit?: (fb: Feedback) => void; language?: "en" | "sv" }> = ({ rubricId, onSubmit, language = "sv" }) => {
  const { t } = useI18n(language);
  const [text, setText] = useState("");
  const [anonymous, setAnonymous] = useState(true);

  const submit = async () => {
    const fb: Feedback = { id: uid("fb"), rubricId: rubricId ?? null, criterionId: null, text, anonymous, createdAt: new Date().toISOString() };
    // save locally
    const existing = (await safeLoad("feedbacks", [])) as Feedback[];
    await safeSave("feedbacks", [...existing, fb]);
    setText("");
    if (onSubmit) onSubmit(fb);
  };

  return (
    <div className="p-3 border rounded" aria-label="Peer feedback">
      <textarea aria-label="Feedback text" value={text} onChange={e => setText(e.target.value)} className="w-full p-2 border rounded" placeholder={t("submitFeedback")}></textarea>
      <div className="flex items-center gap-2 mt-2">
        <label className="flex items-center gap-1"><input type="checkbox" checked={anonymous} onChange={e => setAnonymous(e.target.checked)} /> <span className="text-sm">Anonymous</span></label>
        <button onClick={submit} className="ml-auto px-3 py-1 rounded bg-[var(--primary)] text-white">{t("submitFeedback")}</button>
      </div>
    </div>
  );
};

// 4) PortfolioEvidenceTracker
export const PortfolioTracker: React.FC<{ onAttach?: (e: Evidence) => void; language?: "en" | "sv" }> = ({ onAttach, language = "sv" }) => {
  const { t } = useI18n(language);
  const [items, setItems] = useState<Evidence[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    (async () => setItems((await safeLoad("evidence", [])) ?? []))();
  }, []);

  const attach = async (file?: File) => {
    // For offline-first, we store a blob URL. In prod you'd store blobs in IndexedDB or use service worker cache.
    const id = uid("ev");
    let url;
    if (file) url = URL.createObjectURL(file);
    const e: Evidence = { id, title, description, attachedUrl: url, tags: [], createdAt: new Date().toISOString() };
    const newItems = [e, ...items];
    setItems(newItems);
    await safeSave("evidence", newItems);
    if (onAttach) onAttach(e);
    setTitle("");
    setDescription("");
  };

  return (
    <div className="p-3 border rounded" aria-label="Portfolio tracker">
      <div className="mb-2"><input className="w-full p-2 border rounded" placeholder="Title" value={title} onChange={e => setTitle(e.target.value)} /></div>
      <div className="mb-2"><textarea className="w-full p-2 border rounded" placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} /></div>
      <div className="flex gap-2">
        <input aria-label={t("attachEvidence")} type="file" onChange={e => attach(e.target.files?.[0])} />
        <button onClick={() => attach()} className="px-3 py-1 rounded border">Add (no file)</button>
      </div>

      <div className="mt-4 space-y-2">
        {items.map(it => (
          <div key={it.id} className="p-2 border rounded">
            <div className="font-semibold">{it.title}</div>
            <div className="text-sm text-[var(--muted)]">{it.description}</div>
            {it.attachedUrl && <a href={it.attachedUrl} target="_blank" rel="noreferrer" className="text-xs underline">Open attachment</a>}
          </div>
        ))}
      </div>
    </div>
  );
};

// 5) Offline sync hint component
export const OfflineSync: React.FC<{ onSync?: () => Promise<void> }> = ({ onSync }) => {
  const [online, setOnline] = useState<boolean>(navigator.onLine);
  useEffect(() => {
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  return (
    <div className={`p-2 rounded ${online ? "" : "bg-yellow-100"}`} role="status" aria-live="polite">
      {online ? (
        <div className="flex gap-2 items-center">Online <button className="ml-auto px-2 py-1 border rounded" onClick={() => onSync && onSync()}>Sync now</button></div>
      ) : (
        <div className="flex gap-2 items-center">Offline — your data will be stored locally and synced when online.</div>
      )}
    </div>
  );
};

// ---------- Example App Export ----------

export const DemoApp: React.FC = () => {
  const [lang, setLang] = useState<"sv" | "en">("sv");
  const [rubrics, setRubrics] = useState<Rubric[]>([]);

  useEffect(() => {
    (async () => setRubrics((await safeLoad("rubrics", [])) ?? []))();
  }, []);

  const saveRubric = async (r: Rubric) => {
    const next = [r, ...rubrics.filter(x => x.id !== r.id)];
    setRubrics(next);
    await safeSave("rubrics", next);
  };

  const downloadAll = async () => {
    const rows = rubrics.map(r => ({ id: r.id, title: r.title, criteriaCount: r.criteria.length, createdAt: r.createdAt }));
    exportCSV(rows, "rubrics.csv");
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen p-6 bg-[var(--bg)] text-[var(--text)]">
        <header className="flex items-center gap-4 mb-4">
          <h1 className="text-xl font-bold">Gymnasium Assessment UI</h1>
          <div className="ml-auto flex gap-2">
            <label className="flex items-center gap-1"><input type="radio" checked={lang === "sv"} onChange={() => setLang("sv")} /> SV</label>
            <label className="flex items-center gap-1"><input type="radio" checked={lang === "en"} onChange={() => setLang("en")} /> EN</label>
            <button onClick={downloadAll} className="px-3 py-1 rounded border">Export</button>
          </div>
        </header>

        <main className="grid grid-cols-3 gap-4">
          <div className="col-span-2">
            <RubricBuilder onSave={saveRubric} language={lang} />
            <div className="mt-4">
              <h2 className="font-semibold mb-2">Rubrics</h2>
              <ul className="space-y-2">
                {rubrics.map(r => (
                  <li key={r.id} className="p-2 border rounded flex justify-between items-center">
                    <div>
                      <div className="font-semibold">{r.title}</div>
                      <div className="text-sm text-[var(--muted)]">{r.criteria.length} criteria</div>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => navigator.clipboard.writeText(JSON.stringify(r))} className="px-2 py-1 border rounded">Copy JSON</button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <aside className="col-span-1 space-y-4">
            <OfflineSync />
            <div>
              <h3 className="font-semibold mb-2">Self assessment demo</h3>
              {rubrics[0] ? <SelfAssessmentSlider rubricId={rubrics[0].id} criterion={rubrics[0].criteria[0] ?? { id: "c", title: "No criterion", progressionLevels: [{ level: "1" }, { level: "2" }] }} /> : <div className="text-[var(--muted)]">Create a rubric to see demo</div>}
            </div>

            <div>
              <h3 className="font-semibold mb-2">Peer feedback</h3>
              <PeerFeedbackCollector rubricId={rubrics[0]?.id} language={lang} />
            </div>

            <div>
              <h3 className="font-semibold mb-2">Portfolio</h3>
              <PortfolioTracker language={lang} />
            </div>
          </aside>
        </main>
      </div>
    </ThemeProvider>
  );
};

export default DemoApp;

// ---------- Accessibility notes ----------
// - Buttons and interactive elements have aria-labels, keyboard handlers, and roles where relevant.
// - Ensure color contrast in your theme variables and consider an accessible contrast-checking step in CI.
// - When integrating into a broader app, add skip links and proper heading structure.

// ---------- Next steps for production ----------
// - Split into modules and add tests (Jest/RTL)
// - Add IndexedDB via 'idb' or 'localForage' for robust offline storage
// - Add Service Worker / Workbox to enable full offline PWA functionality and caching
// - Add comprehensive i18n (react-i18next) and pluralization rules
// - Integrate authentication and classroom sync endpoints (optional)
// - Add automated accessibility tests (axe-core)

// License: MIT

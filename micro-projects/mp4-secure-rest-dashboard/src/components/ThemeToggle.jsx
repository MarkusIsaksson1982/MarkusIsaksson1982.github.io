import { useEffect, useState } from "react";
import styles from "./ThemeToggle.module.css";

const STORAGE_KEY = "mp_theme_mode";
const MODES = ["system", "light", "dark"];

function getSystemTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(mode) {
  const root = document.documentElement;
  const resolvedMode = mode === "system" ? getSystemTheme() : mode;

  if (resolvedMode === "dark") {
    root.setAttribute("data-theme", "dark");
  } else {
    root.removeAttribute("data-theme");
  }
}

function readStoredMode() {
  const raw = localStorage.getItem(STORAGE_KEY);
  return MODES.includes(raw) ? raw : "system";
}

function cycleMode(current) {
  const index = MODES.indexOf(current);
  return MODES[(index + 1) % MODES.length];
}

function ThemeToggle() {
  const [mode, setMode] = useState(readStoredMode);

  useEffect(() => {
    applyTheme(mode);
    localStorage.setItem(STORAGE_KEY, mode);

    if (mode !== "system") {
      return undefined;
    }

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = () => applyTheme("system");
    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, [mode]);

  const handleToggle = () => {
    setMode((previous) => cycleMode(previous));
  };

  const label = mode === "system" ? "System" : mode === "light" ? "Light" : "Dark";

  return (
    <button
      type="button"
      className={styles.toggle}
      onClick={handleToggle}
      aria-label={`Theme: ${label}. Activate to switch theme mode.`}
    >
      <span className={styles.mode}>{label}</span>
    </button>
  );
}

export default ThemeToggle;

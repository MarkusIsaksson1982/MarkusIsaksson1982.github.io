import { createContext, useContext, useMemo, useEffect, useCallback } from 'react';
import { useLocalStorage } from '../hooks/useLocalStorage';

/**
 * ThemeContext — separate from AppContext by design.
 *
 * ARCHITECTURAL DECISION: Why two contexts?
 * Theme is consumed by almost every component (for color tokens).
 * If theme were part of AppContext, a tag filter click would cause
 * the theme logic to re-evaluate, and every ThemeContext consumer
 * to re-render unnecessarily. Separation limits re-render blast radius.
 *
 * @type {React.Context<{
 *   theme: string,
 *   setTheme: (t: string) => void,
 *   resolvedTheme: 'light'|'dark',
 *   isDark: boolean,
 *   toggleTheme: () => void
 * } | null>}
 */
const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useLocalStorage('mp3-theme', 'system');

  /**
   * Resolve 'system' → 'light'|'dark' based on media query.
   * Runs synchronously on render — no flash of wrong theme.
   */
  const resolvedTheme = useMemo(() => {
    if (theme !== 'system') return theme;
    if (typeof window === 'undefined') return 'light'; // SSR safety
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }, [theme]);

  /**
   * Apply to <html data-theme="..."> as a side effect.
   * React-idiomatic replacement for MP1's applyTheme().
   * Runs after every resolvedTheme change.
   */
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', resolvedTheme);
  }, [resolvedTheme]);

  /**
   * Listen for OS-level theme changes when user preference is 'system'.
   * Cleanup function removes the listener on unmount or when theme changes.
   */
  useEffect(() => {
    if (theme !== 'system') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    // Re-trigger setTheme with same 'system' value to force resolvedTheme recompute.
    // React batches this so it's not a render loop.
    const handler = () => setTheme('system');
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler); // Cleanup ✓
  }, [theme, setTheme]);

  /** Convenience toggle: light ↔ dark (skips 'system' on toggle) */
  const toggleTheme = useCallback(() => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  }, [resolvedTheme, setTheme]);

  /**
   * Memoized context value — stable reference prevents unnecessary
   * re-renders in ThemeContext consumers.
   */
  const value = useMemo(
    () => ({ theme, setTheme, resolvedTheme, isDark: resolvedTheme === 'dark', toggleTheme }),
    [theme, setTheme, resolvedTheme, toggleTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

/**
 * useTheme — safe ThemeContext consumer with guard clause.
 * Throws if called outside <ThemeProvider> — gives clear error in dev.
 */
export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>');
  return ctx;
}

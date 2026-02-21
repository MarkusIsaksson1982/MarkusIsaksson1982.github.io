import { useState, useCallback } from 'react';

/**
 * useLocalStorage — generic localStorage state hook.
 *
 * Design decisions:
 * 1. Lazy initializer (useState(() => ...)) — reads localStorage ONCE on mount,
 *    not on every render. Critical for performance.
 * 2. Functional setState support — setValue(prev => newVal) mirrors useState API.
 * 3. Try/catch everywhere — localStorage can throw in private browsing (Safari)
 *    and when storage quota is exceeded.
 * 4. SSR guard (typeof window) — safe if Vite SSR is added later.
 *
 * @template T
 * @param {string} key
 * @param {T} initialValue
 * @returns {[T, (value: T | ((prev: T) => T)) => void]}
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    if (typeof window === 'undefined') return initialValue;
    try {
      const item = window.localStorage.getItem(key);
      return item !== null ? JSON.parse(item) : initialValue;
    } catch (e) {
      console.warn(`useLocalStorage: could not read "${key}"`, e);
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value) => {
      try {
        const next = value instanceof Function ? value(storedValue) : value;
        setStoredValue(next);
        window.localStorage.setItem(key, JSON.stringify(next));
      } catch (e) {
        console.warn(`useLocalStorage: could not write "${key}"`, e);
      }
    },
    // storedValue in deps because functional updater reads it
    [key, storedValue]
  );

  return [storedValue, setValue];
}

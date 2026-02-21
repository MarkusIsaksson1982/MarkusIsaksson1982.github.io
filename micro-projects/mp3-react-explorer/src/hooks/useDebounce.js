import { useState, useEffect } from 'react';

/**
 * useDebounce — delays propagation of a value until after `delay` ms of inactivity.
 *
 * React pattern: debounce the VALUE not the handler.
 * This lets components read the debounced value declaratively and React
 * re-renders only when the debounced value actually settles.
 *
 * The cleanup function (return () => clearTimeout) is the React-idiomatic
 * equivalent of MP1's clearTimeout(timer) in a debounce closure.
 * It fires when:
 * - `value` changes (re-runs effect, cancels previous timer)
 * - Component unmounts (prevents setState on unmounted component)
 *
 * @template T
 * @param {T} value
 * @param {number} [delay=300]
 * @returns {T}
 */
export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    // Cleanup: cancel timer if value changes before delay expires
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

import { useRef, useEffect } from 'react';

/**
 * useIntersectionObserver — React-idiomatic wrapper for entrance animations.
 *
 * Pattern: returns a ref to attach to the target element.
 * When element enters viewport, adds `visibleClass` to its classList.
 * Observer disconnects after first trigger (one-shot animation).
 *
 * WHY useRef + useEffect instead of a state variable?
 * Adding a class is a DOM mutation, not state. Using useState would trigger
 * a re-render unnecessarily. useRef + direct classList mutation is the
 * correct React pattern for imperative DOM interactions.
 *
 * The effect cleanup (observer.disconnect) prevents memory leaks when
 * cards unmount (e.g., after filtering changes the visible set).
 *
 * @param {string} visibleClass - CSS class to add when visible
 * @param {{ threshold?: number, rootMargin?: string }} [options]
 * @returns {React.RefObject<HTMLElement>}
 */
export function useIntersectionObserver(
  visibleClass = 'visible',
  { threshold = 0.08, rootMargin = '0px 0px -20px 0px' } = {}
) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.classList.add(visibleClass);
          observer.unobserve(el); // One-shot: stop watching after first trigger
        }
      },
      { threshold, rootMargin }
    );

    observer.observe(el);
    // Cleanup: disconnect when component unmounts
    return () => observer.disconnect();
  }, [visibleClass, threshold, rootMargin]);

  return ref;
}

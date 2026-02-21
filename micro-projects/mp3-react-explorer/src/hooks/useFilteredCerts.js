import { useMemo } from 'react';

/**
 * useFilteredCerts — memoized filter logic extracted into a custom hook.
 *
 * WHY useMemo here (the interview answer):
 * With 16 certs the CPU cost is negligible. The REAL reason is referential
 * stability: without useMemo, every App render creates a new array reference,
 * which breaks React.memo(CertCard) even when nothing visual changed.
 * useMemo ensures the returned array is the same reference as long as
 * filter criteria are unchanged.
 *
 * WHY serialize activeTags to a string for the dep array:
 * JavaScript Sets do not support value equality — new Set(['a']) !== new Set(['a']).
 * The reducer returns a new Set on every TOGGLE_TAG dispatch, so using the Set
 * reference as a dep would cause a useMemo cache miss even when the *contents*
 * haven't changed. Serializing to a sorted comma-string gives correct value equality.
 *
 * @param {import('../data/certifications').Certification[]} certs
 * @param {string} query
 * @param {string} category
 * @param {Set<string>} activeTags
 * @returns {import('../data/certifications').Certification[]}
 */
export function useFilteredCerts(certs, query, category, activeTags) {
  // Stable dep: serialize Set contents for value equality
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const tagsKey = [...activeTags].sort().join('\x00');

  return useMemo(() => {
    const q = query.toLowerCase().trim();

    return certs.filter(cert => {
      const matchQuery =
        !q ||
        cert.name.toLowerCase().includes(q) ||
        cert.skills.some(s => s.toLowerCase().includes(q)) ||
        cert.note.toLowerCase().includes(q);

      const matchCategory = category === 'all' || cert.category === category;

      // All active tags must be present (AND logic, same as MP1)
      const matchTags =
        activeTags.size === 0 ||
        [...activeTags].every(tag =>
          cert.skills.some(s => s.toLowerCase() === tag.toLowerCase())
        );

      return matchQuery && matchCategory && matchTags;
    });

  // tagsKey instead of activeTags for value-equality dep comparison
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [certs, query, category, tagsKey]);
}

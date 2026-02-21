/**
 * helpers.js — Pure utility functions.
 * No React imports, no side effects. Fully unit-testable.
 */

/**
 * Get display label for a certification category.
 * @param {'legacy'|'new'|'additional'} category
 * @returns {string}
 */
export function getCategoryLabel(category) {
  const labels = { legacy: 'Legacy', new: 'New Curriculum', additional: 'Additional' };
  return labels[category] || category;
}

/**
 * Get all unique tech tags across all certifications, alphabetically sorted.
 * Memoize at call site with useMemo if called in a render path.
 * @param {import('../data/certifications').Certification[]} certs
 * @returns {string[]}
 */
export function getAllTags(certs) {
  return [...new Set(certs.flatMap(c => c.skills))].sort();
}

/**
 * Compute summary statistics for a list of certifications.
 * @param {import('../data/certifications').Certification[]} certs
 * @returns {{ total: number, hours: number, legacy: number, newCurriculum: number }}
 */
export function getStats(certs) {
  return {
    total: certs.length,
    hours: certs.reduce((sum, c) => sum + c.approxHours, 0),
    legacy: certs.filter(c => c.category === 'legacy').length,
    newCurriculum: certs.filter(c => c.category === 'new').length,
  };
}

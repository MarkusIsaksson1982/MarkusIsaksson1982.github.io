# Site audit — 2026-10-28

Scope: https://markusisaksson1982.github.io/ (index, /portfolio/, 11 /layers/ pages, 6 /showcases/ pages).
Tools: source review, curl of all 92 unique links/assets, Lighthouse 12 (mobile emulation) on /, /portfolio/, /showcases/agent-action-gate/, and live freeCodeCamp cert API checks.

## Lighthouse baseline (before fixes, live site)
| Page | Perf | A11y | Best pr. | SEO |
|---|---|---|---|---|
| / | 91 | 92 | 96 | 100 |
| /portfolio/ | 90 | 89 | 96 | 90 |
| /showcases/agent-action-gate/ | 100 | 100 | 96 | 90 |

## Findings by severity

### High (needs Markus's decision)
1. **Cert count mismatch with application materials.** The site claims **16 certifications** (index Layer 1 card, /portfolio/ lead and "all 16 certificates"). The brief/applications say **13**. All 16 cert links verify on freeCodeCamp's API (12 legacy/v7/v8, Legacy Full-Stack, A2 English, B1 English, Foundational C#). 16 − (A2, B1, C#) = 13, so "13" probably means the technical certs. Pick one number for everywhere. Not changed.
2. **Personal Gmail in git history.** HEAD contains no personal Gmail, but `mjisaksson@gmail.com` is the author email on ~1,772 commits and appears in the content of old commits (8b12f27, 54159c5). `markusisaksson.religion@gmail.com` is on 4 commits. Anyone can see this with `git log`. Fixing it means rewriting history and force-pushing, so it's his call. Not done.
3. **No location on the site.** "Stockholm" appears nowhere. Add it if applications claim Stockholm. Not changed.

### Medium (fixed)
4. Broken link: /portfolio/ "freeCodeCamp Profile" → `freecodecamp.org/fccfb1888e4-…` returned 404. Repointed to the verifiable Full-Stack cert page. A public profile URL needs a public fCC username (decision).
5. No meta description on 16 of 19 pages (Lighthouse SEO 90 on /portfolio/ and showcases). Added one to every page.
6. No Open Graph tags on any page (except backups-recovery). Link previews in LinkedIn and email were blank. Added og:type/title/description/url and a canonical link.
7. No `<main>` landmark on 8 pages (portfolio, servers, networking, security, backend-apis, ci-cd-pipelines, 3 showcases). Added.
8. Console 404 on every page from a missing /favicon.ico (Best Practices 96). Added an inline SVG favicon.

### Low
9. Links opened with `target="_blank"` lacked `rel="noopener"` (e.g. all 16 cert cards). Added.
10. The /showcases/ad-audit-mini/ redirect stub had no viewport. Added.
11. Render-blocking Google Fonts CSS (~1.6 s estimated on mobile), LCP ~2.8–2.9 s. Could self-host or use `media=print onload` swap. Not changed (affects the look).
12. /portfolio/ tap targets ("Underpins →" layer links) are too small on mobile. Index has one link in text that is told apart only by color. Not changed (needs CSS design choices).
13. Index screenshots are hot-linked from github.com `raw/` (redirect plus no caching control). Consider copying them into the repo.
14. Showcase pages have no nav or link back to the home page.
15. The repo .git is 247 MB (old mirrored node_modules/build in history). Only affects clone time.

### OK
- All `<img>` have alt text. Every page has `lang`, a viewport, and one h1. The Lighthouse a11y contrast audits passed on the tested pages.
- Every other link returned 200. LinkedIn returns 999 (bot block, normal). fonts.googleapis/gstatic bare hosts are preconnect hints, not links.
- Only contact email on the site: markusisaksson@mail.grokbot.com (agent-action-gate), which is intentional.
- 3,600+ hours is used the same way everywhere.

## Diff summary (branch `audit-2026-10-28`, not pushed)
19 HTML files: meta description, OG tags, canonical, favicon, `rel="noopener"`, `<main>` landmarks, fCC profile link fix, viewport on the redirect stub. Plus this AUDIT.md. No visual or content-claim changes.

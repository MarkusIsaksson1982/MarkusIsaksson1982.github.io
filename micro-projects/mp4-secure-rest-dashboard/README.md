# MP4 - Secure REST Simulator & Analytics Dashboard
**Markus Isaksson | Technical Blueprint (Benjamin Lens)**  
**Status:** React 18 + Vite + Service Worker backend simulator

> A static GitHub Pages app that behaves like a full-stack product: auth, middleware, REST routes, IndexedDB persistence, and analytics, all inside the browser.

## Why MP4 Exists
MP1-MP3 proved UI architecture and vanilla execution.  
MP4 proves backend architecture patterns without cloud infrastructure:
- Express-style routing and middleware
- JWT auth with Web Crypto (HMAC SHA-256)
- PBKDF2 password hashing
- IndexedDB schema + transactions
- Audit logging + analytics aggregation

## Stack
- React 18
- Vite 5
- React Router (`HashRouter`)
- Service Worker module backend (`public/sw/**`, sourced from `sw/**`)
- IndexedDB (no localStorage for app data)
- Pure SVG charts (no chart libraries)
- Design tokens inherited from MP1-MP3

## Quick Start
1. Install deps:
```bash
npm install
```
2. Start dev:
```bash
npm run dev
```
3. Open `http://localhost:5173` (or Vite-assigned port)
4. Demo login:
- username: `demo`
- password: `demo1234`

## GitHub Pages Base Path
Vite base path is configurable:
- local dev default: `VITE_BASE_PATH=/`
- project pages example: `VITE_BASE_PATH=/micro-projects/mp4-rest-dashboard/`

Create `.env` from `.env.example` when you need a non-root base.

Service worker registration in `src/App.jsx` uses `import.meta.env.BASE_URL` for both:
- script URL
- SW scope

This is required for non-root deployments.

## Project Order (Frontend)
```
src/
  main.jsx
  App.jsx
  contexts/
    AuthContext.jsx
  hooks/
    useTasks.js
    useAnalytics.js
  pages/
    LoginPage.jsx
    TasksPage.jsx
    AnalyticsPage.jsx
  components/
    ProtectedRoute.jsx
    ThemeToggle.jsx
    FilterBar.jsx
    TaskForm.jsx
    TaskCard.jsx
    charts/
      TrendChart.jsx
      StatusBreakdown.jsx
      Heatmap.jsx
      ProductivityScore.jsx
  tokens/
    design-tokens.css
```

## Service Worker File Order
Source backend files live in:
```
sw/
  sw.js
  router.js
  middleware/
  routes/
  db/
  utils/
```

Before `dev`, `build`, and `preview`, `npm run sync:sw` copies `sw/**` to `public/sw/**`.
Vite serves `public/sw/**` as static module files.

## Integration Test
Playwright smoke test:
```bash
npm run test:integration
```

Covered flow:
1. Service worker controls the page
2. Register a new user
3. Create a task
4. Open analytics and verify API responses

## Accessibility & UX
- Keyboard-accessible forms and navigation
- `skip-link` and `visually-hidden` utilities
- WCAG-conscious color contrast with inherited token palette
- `prefers-reduced-motion` respected globally and in chart animations

## AI Orchestration Transparency Log
- **Service Worker backend architecture and implementation:** Codex (GPT-5 coding agent)
- **React frontend shell, hooks, pages, components, and SVG charts:** Codex (GPT-5 coding agent)
- **Integration hardening (base path + SW sync + Playwright smoke):** Codex (GPT-5 coding agent)

This log is intentionally explicit to make model/task allocation reviewable.

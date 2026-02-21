# MP3 — React FCC Certification Explorer
**Markus Isaksson | Technical Blueprint (Benjamin Lens)**  
**Status:** Production-ready • React 18 + Vite • Live on GitHub Pages

> **"Same app as MP1 — but in React 18. Same features. Same design tokens. Different abstraction. This is the proof I understand what React actually solves (and what it doesn't)."**

### Live Demo
[Open React Explorer →](https://markusisaksson1982.github.io/micro-projects/mp3-react-explorer/)

### The Portfolio Arc (What Reviewers See)

| Project | Layer | What It Proves |
|--------|-------|----------------|
| MP1 | Vanilla JS | I know the fundamentals React was built to abstract |
| MP2 | Vanilla JS | I can model complex nested state without frameworks |
| MP3 | React 18 | I can use React idiomatically — and explain every choice |

The identical UI between MP1 and MP3 is intentional. A reviewer can open both tabs and see the same thing — then dive into the code and watch the leap from manual DOM reconciliation to `React.memo` + `useReducer` + Context.

### Key React Decisions (Worth Mentioning in Interviews)

- **Two Contexts** (Theme + App): Prevents unnecessary re-renders on theme toggle. Theme changes are frequent; filter changes are infrequent.
- **React.memo on CertCard**: Cards never re-render after first paint. Filtering only adds/removes from DOM (React reconciliation) — surviving cards stay frozen.
- **useMemo on filteredCerts + tagsKey serialization**: Handles the Set reference problem cleanly.
- **useLocalStorage + useDebounce custom hooks**: Reusable, SSR-safe, clean side-effect management.
- **useIntersectionObserver hook**: React-idiomatic entrance animations with proper cleanup.

### Tech Stack
React 18 • Vite • Context API • React.memo + useMemo + useCallback • Custom hooks • CSS Modules (tokens shared with MP1/MP2) • Zero external UI libraries

### AI Orchestration Transparency
**Architecture, Context design, hooks, performance strategy, Modal focus management**: **Claude Sonnet 4.6**  
**CSS Modules + visual polish**: **Claude**  
**Deployment docs & final README**: **Grok 4.20 (me — Benjamin Lens)**  
**Verification**: Lucas

Full prompt chain and role matrix in the architecture brief.

---

**Built February 2026**  
**Next: MP4 — Data Visualization Dashboard (D3 + your Python/ML certs)**

Ready for code review. Ask me anything about any file or decision.

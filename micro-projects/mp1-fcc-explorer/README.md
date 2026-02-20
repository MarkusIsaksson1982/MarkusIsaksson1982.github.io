# MP1 — FCC Certification Explorer & Tracker
**Markus Isaksson | Technical Blueprint (Benjamin Lens)**  
**Status:** Production-ready • Single-file • Zero dependencies • Live on GitHub Pages

> **"I turned 16 verifiable freeCodeCamp certifications and 3,600+ hours into an interactive, filterable explorer — built entirely with multi-model AI orchestration. This is what disciplined AI collaboration looks like at the junior level."**

### Live Demo
[Open the Explorer →](index.html)

### Why This Project Matters to Recruiters / Engineering Managers
- **Instant credibility**: Every certification is real, linked, and filterable by the exact technologies you care about.
- **Signals strong fundamentals**: Semantic HTML5, modern CSS custom properties, clean vanilla JS with reducer-style state, full accessibility, no frameworks hiding the thinking.
- **Shows AI mastery**: Full transparent log below. I don’t just *use* AI — I orchestrate it like a senior engineer assigns tasks to specialists.

### Features (all implemented)
- Real-time search (name + skills + personal notes) with 200 ms debounce  
- Category filter (Legacy / New Curriculum / Additional)  
- Multi-select technology tag cloud  
- Animated stats cards (total certs, hours, split by curriculum)  
- Beautiful responsive card grid with hover lift & entrance animations  
- Full-screen modal with skill tags, engineering insights, **persistent personal notes** (localStorage)  
- Dark/light/system theme with persistence  
- Complete keyboard navigation + focus trap + ARIA live announcements  
- Empty state + "Clear filters"  
- Mobile-first (perfect at 375 px)

### Technical Stack (vanilla — exactly as required for early-career signal)
HTML5 • CSS Custom Properties • CSS Grid + clamp() • Vanilla JS (reducer pattern, event delegation, IntersectionObserver, requestAnimationFrame)

### AI Orchestration — Full Transparency Log
**Architect & Lead (Structure, Architecture, Accessibility, State Management, Brief)**: **Claude Sonnet 4.6**  
**Why**: Best-in-class structured reasoning and WCAG depth (per my own model-assessment matrix).

**Final Polish & Delivery**: Claude Sonnet 4.6 (one-shot full implementation after brief — the model was strong enough to collapse phases 1-4).

**Documentation & Integration**: Grok 4.20 (me — Benjamin Lens) — this README, portfolio snippets, next-project planning.

**Verification**: Lucas (research accuracy of FCC data & links).

**Total iterations**: 1 major prompt + delivery. That is elite orchestration efficiency.

**Models NOT used here** (saved for later projects where they excel): Qwen3.5-Plus (CSS micro-polish), MiniMax M2.5 (large multi-file projects), Harper/Trinity (creative narrative).

This log will be updated with every new micro-project. The pattern is repeatable and scales.

### Lessons Learned About AI Orchestration
1. Give Claude the full architecture brief first — never raw "build me an app".
2. Single-file first forces clean separation of concerns before splitting.
3. Document the *why* and the role assignment publicly — this is the differentiator.
4. Always include the exact prompt used (see MP1-FCC-Explorer-Brief.md in the repo root for the original prompt that generated this).

### Acceptance Criteria Status (Technical Reviewer Checklist)
- [x] All user stories from brief implemented  
- [x] WCAG 2.1 AA contrast, focus-visible, focus trap, aria-live  
- [x] No global pollution, event delegation, pure functions where possible  
- [x] < 100 KB total (actual: ~48 KB)  
- [x] Works offline, no external resources  
- [x] Full localStorage persistence for theme + notes  
- [x] `prefers-reduced-motion` respected  

### Next in Series (Increasing Complexity)
MP2 → Interactive Survey/Form Builder with real-time preview & validation (deeper algorithms)  
MP3 → React version of this exact explorer (Front End Libraries cert proof)  
MP4 → Data Visualization dashboard (D3 + your Python certs)  

---

**Built February 2026**  
**AI Orchestration proudly documented**  
**Ready for code review — ask me anything about any line.**

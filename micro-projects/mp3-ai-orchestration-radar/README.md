# MP3 — AI Orchestration Radar
**Markus Isaksson | Technical Blueprint**  
**Status:** Production-ready • Single-file • Zero dependencies • Live on GitHub Pages

> **"I built an interactive data visualisation dashboard that renders my own AI model assessment data as radar charts, comparative rankings, and orchestration strategy recommendations — all in vanilla SVG + JS. The tool that visualises AI orchestration is itself a product of AI orchestration. This is the meta-layer."**

### Live Demo
[Open the Radar →](index.html)

### Why This Project Matters to Engineering Reviewers
- **New skill paradigm**: MP1 = read/filter. MP2 = create/mutate. MP3 = **visualise and analyse**. The trilogy covers three fundamental interaction patterns.
- **Data Visualisation cert in action**: SVG radar charts, dynamic bar charts, interactive data points with tooltips — the D3.js concepts (data binding, scales, coordinate geometry) implemented from scratch in vanilla JS.
- **Self-referential**: The dashboard visualises AI model comparison data from a real engineering task. The content IS the orchestration narrative.
- **Adjacent skills demonstrated**: Trigonometric coordinate math (college algebra cert), JSON data processing (data analysis cert), analytical reasoning (ML cert patterns), all without any framework.

### Features (all implemented)
- Interactive SVG radar/spider chart with per-dimension model comparison
- Toggle models on/off with chip selector (minimum 1 active)
- Animated score ranking bars with percentage fills
- Model profile cards with strengths, weaknesses, and recommended use cases
- Cross-model shared flaw analysis table
- Orchestration strategy cards (task-to-model routing recommendations)
- Hover tooltips on radar data points
- Dark/light/system theme with persistence (identical tokens to MP1/MP2)
- Complete keyboard navigation + ARIA announcements
- IntersectionObserver staggered reveal animations
- prefers-reduced-motion respected
- Mobile-first responsive (perfect at 375px)

### Technical Stack (vanilla — deliberate continuation of series)
HTML5 • SVG (hand-computed radar geometry) • CSS Custom Properties (100% MP1/MP2 tokens) • Vanilla JS (reducer-style state, event delegation, dynamic SVG generation, IntersectionObserver)

### Data Source
Assessment data embedded from [`assessment-data-claude-sonnet-4.6.json`](../../model-assessments/assessment-data-claude-sonnet-4.6.json) — a real multi-model comparison of JWT + Redis auth service implementations across 8 rubric dimensions. Per-dimension scores derived from the strengths/weaknesses analysis in that assessment.

### Complexity Progression Across the Series

| Aspect | MP1 (Explorer) | MP2 (Builder) | MP3 (Radar) |
|--------|----------------|---------------|-------------|
| Data flow | Static → read | Dynamic → CRUD | Structured → visualise |
| State | Filters + search | Nested questions + drafts | Model selection + SVG recompute |
| DOM work | Card grid + modal | Selective reconciliation | Dynamic SVG generation |
| Key skill | Filtering & a11y | Validation & persistence | Data viz & coordinate math |
| Cert area | Responsive Web | JS Algorithms | Data Visualisation + Algebra |

### AI Orchestration — Full Transparency Log
**Architecture, SVG Geometry, State Design, Full Implementation**: **Claude Opus 4.6**  
**Why**: Strong structured reasoning, SVG coordinate math, and ability to maintain 100% token inheritance across a complex single-file build.

**Assessment Data**: Originally produced by **Claude Sonnet 4.6** (the model comparison assessment itself).

**Documentation & Portfolio Integration**: **Claude Opus 4.6** — this README, portfolio card updates, orchestration narrative.

**Total iterations**: Architecture brief → full working dashboard. The orchestration pattern from MP1/MP2 continues to prove repeatable.

### Skills Demonstrated Beyond Direct Certifications
This project deliberately showcases **adjacent skills** — abilities that naturally follow from the documented 3,600+ hours but aren't individually certified:

- **SVG programming**: Not a separate cert, but direct extension of D3.js Data Visualisation (300 hrs)
- **Trigonometric coordinate geometry**: Applied from College Algebra with Python cert
- **Structured data analysis**: Pattern from Data Analysis with Python cert applied to JSON assessment data
- **Analytical reasoning about AI outputs**: ML cert gives the vocabulary; this project applies it to model evaluation
- **Design system inheritance**: Maintaining 100% token compatibility across 3 projects signals architectural discipline

### Acceptance Criteria Status (Technical Reviewer Checklist)
- [x] SVG radar chart renders correctly with all active models
- [x] Model toggling updates radar, ranking, and card highlights reactively
- [x] Tooltips show dimension name + score on hover
- [x] WCAG 2.1 AA: contrast, focus-visible, aria-live, skip link
- [x] Identical design tokens to MP1/MP2 (verified)
- [x] < 50 KB total (actual: ~41 KB)
- [x] Works offline, zero external resources
- [x] prefers-reduced-motion respected
- [x] Mobile-first responsive

### What This Tells You About Orchestration Skills
1. **Task decomposition**: Knowing which model to assign to which sub-task (production code vs. documentation vs. security review)
2. **Cross-model verification**: Using multiple models on the same task to catch shared blind spots
3. **Strength-based routing**: Not defaulting to "best model for everything" — assigning by dimension match
4. **Transparent documentation**: Every decision logged publicly. The process is the product.

---

**Built March 2026**  
**AI Orchestration proudly documented**  
**Ready for code review — ask me anything about any line.**

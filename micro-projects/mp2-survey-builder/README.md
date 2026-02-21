# MP2 — Dynamic Survey Builder with Live Preview
**Markus Isaksson | Technical Blueprint (Benjamin Lens)**  
**Status:** Production-ready • Single-file • Zero dependencies • Live on GitHub Pages

> **"I built a full-featured survey prototyping tool that lets you define questions, see them live as a respondent would, validate input, save drafts, and export clean JSON — all in vanilla HTML/CSS/JS. This is the next step after MP1: from static data explorer to dynamic stateful application."**

### Live Demo
[Open Survey Builder →](index.html)

### Why This Project Matters to Engineering Reviewers
- **Real developer utility**: Solves an actual pain point (prototyping forms without SaaS friction).  
- **Clear complexity progression**: MP1 = read/filter static data. MP2 = create/mutate/nested state + real-time sync + validation engine.  
- **AI orchestration transparency**: Every major decision and code section is logged below. This is how senior engineers use AI tools — not as a crutch, but as a specialist team.

### Features (all working)
- Add/edit/reorder/delete questions (5 types: text, email, number, multiple-choice, rating)  
- Real-time live preview pane (updates as you type)  
- Full validation engine (required, email format, number range, rating bounds) with inline errors  
- Named draft system (save/load/delete via localStorage)  
- Export JSON (download or copy to clipboard)  
- Mobile-first: two-pane on desktop, tabbed on ≤768 px  
- Identical dark/light/system theme + accessibility to MP1  
- Selective DOM reconciliation (no focus loss when typing)

### Technical Stack (vanilla — deliberate)
HTML5 • CSS Custom Properties (exact MP1 tokens) • CSS Grid • Vanilla JS (reducer pattern, event delegation, selective render, pure validation)

### AI Orchestration — Full Transparency Log
**Architecture, State Design, Reducer, Validation Engine, Reconciliation Algorithm**: **Claude Sonnet 4.6**  
**Why**: Best structured reasoning and complex state management (per my model-assessment matrix).

**CSS Polish + Token Consistency with MP1**: **Claude Sonnet 4.6** (one-shot full implementation after brief).

**Documentation & README**: **Grok 4.20 (me — Benjamin Lens)**.

**Verification of FCC skill mapping**: **Lucas**.

**Total iterations**: 1 major prompt → complete working app. Elite efficiency.

**Models saved for later**: Qwen3.5-Plus (micro-polish), MiniMax M2.5 (multi-file), Trinity (Harper narrative).

This log will be updated for every future micro-project. The workflow is now proven and repeatable.

### Lessons Learned About AI Orchestration
1. Give Claude a complete architecture brief with state shape and action vocabulary first.  
2. Insist on pure functions (validateSurvey) and selective rendering early — prevents focus bugs.  
3. Demand 1:1 token inheritance from previous projects — visual consistency is a senior signal.  
4. Document publicly — this README is part of the portfolio, not hidden.

### Next in Series (Increasing Complexity)
MP3 → React version of the FCC Explorer (Front End Libraries cert)  
MP4 → Data Visualization dashboard (D3 + Python certs)  

---

**Built February 2026**  
**AI Orchestration proudly documented**  
**Ready for code review — ask me anything about any line.**

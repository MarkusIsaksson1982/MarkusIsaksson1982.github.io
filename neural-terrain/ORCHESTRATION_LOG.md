# Orchestration Log — Neural Terrain

## Project Summary

**Neural Terrain** is an interactive procedural terrain generator built entirely through multi-model AI orchestration. Four distinct AI models each contributed specialized code that was tested, evaluated, and integrated into a unified browser-based demo.

The purpose is not just the terrain generator itself, but demonstrating that **AI orchestration is a skill** — involving architecture decisions, quality evaluation, integration engineering, and knowing which model to assign to which task.

---

## Models Used

| Model | Interface | Role | Phase 1 | Phase 2 |
|-------|-----------|------|---------|---------|
| **Claude Opus 4.6** | claude.ai | Orchestrator | Designed all architecture, prompts, test suites, and evaluation rubrics | Integration, frontend, pipeline, this document |
| **Gemini 3.0 Pro** | Gemini CLI v0.28.2 | Noise algorithms | 100% (2 attempts) | Simplex: 100% (1 attempt) |
| **gpt-5.3-codex** | OpenAI Codex CLI v0.101.0 | Hydraulic erosion | 100% (2 attempts) | Erosion: 95% (1 attempt) |
| **Grok 4.1** | Web | Biome classification | 100% (2 attempts) | Biome: 100% (1 attempt) |

---

## Timeline

### Phase 1: Foundational Assessment (Day 1)

**Goal**: Calibrate model capabilities using a standardized Perlin noise implementation task.

All six candidate models were considered. Three were prioritized based on estimated capability:

1. Gemini 3.0 Pro, gpt-5.3-codex, and Grok 4.1 were tested first
2. All three reached 100% on the 25-test suite within 2 iterations
3. The remaining three models (GLM-5, Big Pickle, Kimi K2.5) were not needed

**Key observation**: All three models made the same initial mistake — over-normalizing the octave noise accumulation, which reduced variance. All self-corrected when given the failing test output. This suggests the prompt's octave specification could have been clearer, but also demonstrates the value of test-driven iteration.

**Differentiation**: Gemini 3.0 Pro scored highest on code quality (5/5) due to proper `random.Random` isolation and PEP8 compliance. gpt-5.3-codex and Grok 4.1 scored 4/5.

### Phase 2: Specialized Tasks (Day 1, continued)

Based on Phase 1 results, tasks were assigned to play to each model's strengths:

| Task | Model | Rationale |
|------|-------|-----------|
| Simplex Noise | Gemini 3.0 Pro | Highest code quality, strong math — simplex requires careful skew/unskew |
| Hydraulic Erosion | gpt-5.3-codex | Strong algorithmic code via CLI — erosion needs complex simulation loops |
| Biome Classification | Grok 4.1 | Web-only interface suits self-contained files; structured logic task |

**Results**:
- **Gemini**: 100% on 27 simplex tests, first attempt. Flawless.
- **gpt-5.3-codex**: 95% on 22 erosion tests, first attempt. The one failure was a gradient convention mismatch (test expected downhill-pointing gradient; code uses mathematical convention with negation in the simulation loop). All 5 physics tests passed — the erosion actually works correctly.
- **Grok**: 100% on 42 biome tests, first attempt. Including 180 boundary-value combinations.

### Phase 3: Integration (Day 1-2)

Claude Opus 4.6 handled:

1. **Code review** of all four implementations, running test suites
2. **JavaScript port** of all algorithms for the browser demo
3. **Pipeline design** — connecting noise → erosion → biome classification
4. **Interactive frontend** — 512×512 canvas with real-time parameter controls
5. **This document** — the orchestration narrative

---

## Architecture Decisions

### Why These Three Models (Not All Six)?

Three models covered the entire pipeline. Adding more would have:
- Increased integration complexity without proportional quality gains
- Required reconciling different code styles and conventions
- Diluted the narrative (harder to explain the role of each model)

The principle was: **use fewer models well, rather than many models poorly**.

### Why These Task Assignments?

- **Gemini → Noise**: Mathematical algorithms benefit from rigorous implementations. Gemini demonstrated the best adherence to algorithm specifications and cleanest code.
- **Codex → Erosion**: The most algorithmically complex task, involving particle simulation with boundary checking, bilinear interpolation, and brush kernels. CLI access made iteration efficient.
- **Grok → Biome**: A structured logic task (if/else classification) that is self-contained in a single file — ideal for web-only interfaces where file management is limited.

### The Gradient Convention Issue

gpt-5.3-codex's erosion implementation computes gradients using the standard mathematical convention (∇h points uphill). The simulation loop then negates it: `direction = old * inertia - gradient * (1 - inertia)`. This is correct behavior — all physics tests pass. The test expected "gradient points downhill" per the docstring, but the code uses the standard convention with explicit negation. This was classified as a non-blocking test/spec mismatch, not a code bug.

---

## Quality Assurance

### Test-Driven Development

Every component had a test suite designed before the implementation prompt was written. Test suites were designed to verify:

| Category | What It Catches |
|----------|----------------|
| API conformance | Wrong class/method signatures |
| Value range | Output exceeding specified bounds |
| Determinism | Non-reproducible randomness |
| Continuity | Discontinuities, grid artifacts |
| Physical correctness | Mass conservation, erosion behavior |
| Edge cases | Boundary values, small inputs |
| Performance | Unacceptable runtime |

### Scoring Rubric

Each implementation was scored on a 100-point scale:
- 40 points: test pass rate
- 20 points: code quality (readability, types, docs)
- 15 points: algorithm-specific correctness
- 15 points: API conformance
- 10 points: performance

Required gates: value range and gradient continuity must pass regardless of score.

### Iteration Protocol

Each model got up to 3 attempts. On failure, the test output was fed back with a request to fix. Most models needed exactly 2 attempts (initial + one fix for octave normalization). Phase 2 tasks were mostly one-shot.

---

## What The Orchestrator Contributed

Claude Opus 4.6's role was not "just prompting." It involved:

1. **Project conception** — choosing a project that genuinely benefits from multi-model collaboration
2. **Architecture** — designing the pipeline stages, file structure, and integration plan
3. **Prompt engineering** — writing precise implementation specs that different models could follow compatibly
4. **Test suite design** — 114 total tests across all components, with mathematical property verification
5. **Evaluation framework** — scoring rubric, iteration protocol, advancement criteria
6. **Code review** — running tests, analyzing failures, determining which are blocking vs. non-blocking
7. **Integration** — porting four Python implementations to JavaScript, resolving convention differences
8. **Frontend development** — building the interactive demo with real-time rendering
9. **Documentation** — this orchestration narrative

---

## File Manifest

| File | Author | Description |
|------|--------|-------------|
| `index.html` | Claude Opus 4.6 | Interactive demo (JS ports of all algorithms) |
| `ORCHESTRATION_LOG.md` | Claude Opus 4.6 | This file |
| `README.md` | Claude Opus 4.6 | Project overview |
| `python/terrain/noise.py` | Gemini 3.0 Pro | Perlin noise (Python reference) |
| `python/terrain/simplex.py` | Gemini 3.0 Pro | Simplex noise (Python reference) |
| `python/terrain/erosion.py` | gpt-5.3-codex | Hydraulic erosion (Python reference) |
| `python/terrain/biome.py` | Grok 4.1 | Biome classification (Python reference) |
| `python/terrain/pipeline.py` | Claude Opus 4.6 | Unified pipeline |
| `python/tests/test_noise.py` | Claude Opus 4.6 | Perlin noise tests (25 tests) |
| `python/tests/test_simplex.py` | Claude Opus 4.6 | Simplex noise tests (27 tests) |
| `python/tests/test_erosion.py` | Claude Opus 4.6 | Erosion tests (22 tests) |
| `python/tests/test_biome.py` | Claude Opus 4.6 | Biome tests (42 tests) |

---

## Conclusion

This project demonstrates that effective AI-assisted development involves:

- **Judgment**: Choosing which models to use and which to skip
- **Evaluation**: Objective testing with clear pass/fail criteria
- **Integration**: Making independently-developed components work together
- **Quality control**: Understanding when a test failure is a real bug vs. a specification mismatch
- **Architecture**: Designing systems that can be built by multiple contributors

The terrain generator works. But the real deliverable is the process.

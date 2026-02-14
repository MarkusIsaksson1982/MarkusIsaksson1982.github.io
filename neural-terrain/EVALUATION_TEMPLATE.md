# Model Evaluation: [MODEL NAME HERE]

**Date**: [YYYY-MM-DD]  
**Task**: Perlin Noise Implementation (Phase 1 Assessment)  
**Interface**: [CLI name + version / Web]  
**Iterations used**: [1 / 2 / 3]

---

## Test Results

| Attempt | Tests Passed | Tests Failed | Total | Pass Rate |
|---------|-------------|-------------|-------|-----------|
| 1       |             |             |       |        %  |
| 2       |             |             |       |        %  |
| 3       |             |             |       |        %  |

### Failing Tests (final attempt)

List each failing test and a brief reason:

- `test_name_here` — [reason]
- `test_name_here` — [reason]

---

## Scoring Rubric

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| Test pass rate (pass_rate × 40) | | 40 | |
| Value range correctness (required) | PASS / FAIL | — | Output in [-1,1] for noise, [0,1] for grid |
| Gradient continuity (required) | PASS / FAIL | No discontinuities at integer boundaries |
| Code quality (1-5 scale, ×4) | | 20 | Readability, naming, types, docstrings |
| Performance: 512×512 grid | | 10 | 10 if <5s, 5 if <10s, 0 if >10s |
| Octave/fBm implementation | | 15 | Correct persistence, lacunarity, stacking |
| API conformance | | 15 | Exact class name, method signatures, return types |
| **TOTAL** | **___** | **100** | |

### Required criteria check

- [ ] Value range: PASS
- [ ] Gradient continuity: PASS

If either required criterion fails → automatic cap at "CONDITIONAL" regardless of score.

---

## Verdict

Mark one:

- [ ] **ADVANCE** (score ≥ 70, both required criteria pass) → Assign Phase 2 task
- [ ] **CONDITIONAL** (score 60-69, or one required criterion marginal) → Usable with manual fixes
- [ ] **EXCLUDE** (score < 60, or required criterion hard-fail) → Do not use further

---

## Code Quality Observations

**Strengths**:
- 

**Weaknesses**:
- 

**Style notes** (naming conventions, structure, documentation):
- 

---

## Recommended Phase 2 Role

If advancing, this model should work on:

- [ ] Simplex Noise (Task A) — good for models with strong math
- [ ] Hydraulic Erosion (Task B) — good for models with clean algorithmic code
- [ ] Thermal Erosion (Task C) — good for solid but not top-tier models
- [ ] Biome Classification (Task D) — good for models with structured logic
- [ ] Worley/Voronoi Noise (Task E) — good for models with geometric reasoning

**Reasoning**: [Why this assignment?]

---

## Raw Notes

[Any additional observations, quirks, or interesting behaviors during the assessment]

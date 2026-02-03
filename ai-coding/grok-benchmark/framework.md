# Grok Benchmarking Framework v1.0

## Core Evaluation Axes
7 axes, ranked by objectivity (most to least). Total score per prompt: Sum of axis points (e.g., ~30-35 max).

1. **Functional Correctness** (Objective: Test pass rate, 0-10 pts)
   - Does code meet spec? Runtime errors = heavy penalty.

2. **Boundary & Edge-Case Handling** (Checklist-based, 0-6 pts)
   - Handles degenerates (e.g., empty input, malformed data)? Penalty for crashes.

3. **Algorithmic Judgment** (0-4 pts: Claim correctness 0/1, Appropriateness 0-2, Justification 0/1)
   - Appropriate time/space? Penalize wrong claims or inefficiency.

4. **Security & Robustness** (Task-specific checklist, 0-5 pts)
   - Input validation, error handling? Binary Y/N items.

5. **Debugging & Comprehension** (0-6 pts: Diagnosis accuracy 0-3, Fix minimalism 0-3)
   - Diagnoses root cause in broken code? Tests reading vs. pattern-matching.

6. **Spec & Format Compliance** (0-6 pts: Deductions for violations)
   - Follows output format? Penalties for hallucinations, overengineering.

7. **Reasoning Transparency & Verification** (Checklist 0-5 pts)
   - States complexity with justification (0/1), Mentions tradeoff (0/1), Identifies failure mode (0/1), Provides verification (tests/reasoning, 0-2).

## Design Rationale
- **Objectives**: 6-12 prompts total, increasing tiers, minimal ambiguity, offline judging.
- **OpenCode Constraints**: Single-shot (mostly), temperature=0.0, max_tokens=4096, no browsing/retries. Truncations scored as failures.
- **Scoring Rubrics**: Partial credit, penalties for unsafe code/hallucinations. Blind, double-score subjective axes.
- **Stress Archetypes**: Data pipeline, algorithmic debug, security wrapper (see prompts).
- **Statistical Signal**: 10 prompts ideal for detecting 15% gaps.
- **Inter-Rater Reliability**: Single-rater for objective axes, double-blind for subjective. Anonymize outputs.
- **Failure Modes to Detect**: GIL confusion, shotgun fixes, library hallucinations (2025-26 LLMs often overengineer or misclaim complexity).

## Expansion Plan
Start with 3 prompts. If pilots show good spread, add: Refactoring, multi-file, test generation tasks.

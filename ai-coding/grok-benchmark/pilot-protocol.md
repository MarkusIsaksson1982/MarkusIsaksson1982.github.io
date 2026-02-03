# Pilot Testing Protocol

## Setup
- OpenCode v1.1.49, temp=0.0, max_tokens=4096, no retries.
- Command: opencode run --model <MODEL> --prompt-file <PROMPT> --output results/<MODEL>_<TIER>.json

## Phase 1: 2 Models
- Strong: Trinity Large Preview
- Weak: GLM-4.7 Free
- Run all 3 prompts, score blindly.

## Phase 2: All 5 Models
- If Phase 1 gap ≥15pts, proceed.

## Scoring
- Use rubrics in prompt files.
- Double-score Axis 7.
- Analyze: Means, gaps, variances.

## Validation
- Spread good? Refine if clustering.
- Disclose versions, dates.

# Grok Benchmark for Coding Models in OpenCode Zen

This folder contains Grok's independent methodology for benchmarking the following coding models in OpenCode Zen v1.1.49:
- Kimi K2.5 Free
- Trinity Large Preview
- Big Pickle
- MiniMax M2.1 Free
- GLM-4.7 Free

## Overview
The goal is to co-design (and eventually run) a rigorous, small-scale benchmark suite (starting with 3 tiered prompts, expandable to 10-12). This focuses on methodology design, not direct benchmarking yet. Key elements:
- **7 Evaluation Axes**: Ranked by objectivity, with scoring rubrics.
- **Benchmark Suite**: 3 initial prompts (Easy, Medium, Hard tiers) stressing different skills.
- **OpenCode Constraints**: CLI-driven, single-shot prompts, temperature=0.0, max_tokens=4096, no retries.
- **Scoring**: Numerical with partial credit, penalties for hallucinations/overengineering.
- **Pilot Protocol**: Run 2 models first (e.g., Trinity as strong, GLM as weak), then all 5. Blind scoring with inter-rater checks.

This is self-contained for resumption: All files reference the framework and can be used standalone.

## Files
- `framework.md`: Core axes, rubrics, and design rationale.
- `prompts/tier-easy.md`: Easy-tier prompt (CSV Transformer) with rubric.
- `prompts/tier-medium.md`: Medium-tier prompt (Log Aggregator) with rubric.
- `prompts/tier-hard.md`: Hard-tier prompt (Concurrency Debug) with rubric.
- `pilot-protocol.md`: Instructions for running pilots.

## Next Steps
- Run pilots as described in `pilot-protocol.md`.
- Expand to 10 prompts if pilots validate (e.g., add refactoring, API design tasks).
- For updates to OpenCode (e.g., beyond v1.1.49), re-run with version disclosure.

This methodology emphasizes engineering judgment over algorithmic recall, with honeypots for common LLM failures (e.g., library misuse, overengineering).

# Gemini 3.0 Pro Benchmarking Framework (v1.0)

This framework is adapted from the ChatGPT-5.2 / Claude Sonnet 4.5 consensus methodology to assess 'Gemini 3.0 Pro' within the 'Gemini CLI' environment.

## 1. Evaluation Axes
Models are scored across 7 axes for every task:
1. [cite_start]**Functional Correctness**: Pass rate of hidden and visible test cases[cite: 5, 15].
2. [cite_start]**Boundary & Failure Handling**: Graceful handling of malformed input, empty sets, and edge conditions[cite: 5, 18].
3. [cite_start]**Algorithmic Judgment**: Appropriateness of Big-O complexity and accuracy of the model's complexity claims[cite: 6, 8].
4. [cite_start]**Security & Robustness**: Adherence to a task-specific security checklist (e.g., input sanitization, PII safety)[cite: 6, 11].
5. [cite_start]**Code Archaeology (Debugging)**: (Hard Tier only) Accuracy of bug diagnosis and quality of minimal-intervention fixes[cite: 6, 14, 15].
6. [cite_start]**Spec & Format Compliance**: Adherence to CLI constraints, JSON schemas, and prohibited libraries (e.g., no Pandas)[cite: 6, 12].
7. [cite_start]**Reasoning Transparency & Self-Verification**: A 0-5 checklist scoring complexity justification, tradeoff discussion, and verification plans[cite: 8, 9, 11].

## 2. Execution Parameters
- **Model**: `Gemini 3.0 Pro`
- **Interface**: `Gemini CLI` (v0.26.0)
- [cite_start]**Temperature**: `0.0` (Deterministic) [cite: 12]
- [cite_start]**Max Tokens**: `4096` [cite: 12]
- **Protocol**: Single-shot for Easy/Medium; [cite_start]One-turn "repair" cycle permitted for Tier-Hard if initial tests fail[cite: 12, 13].

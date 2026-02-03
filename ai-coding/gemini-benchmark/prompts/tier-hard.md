# TASK: Distributed Cache Bug Hunt
You are provided with a Python implementation of an LRU Cache using `collections.OrderedDict` and `threading.Lock`. It is failing under high-concurrency load.

SYMPTOMS:
- Intermittent `KeyError` during `get()`.
- `put()` operations occasionally result in the cache exceeding its capacity.
- Heisenbug behavior: The issue disappears when `print()` statements are added.

REQUIRED ACTIONS:
1. Identify the root cause (focus on atomicity of compound operations).
2. Provide a MINIMAL patch (<15 lines of code) to fix the race condition.
3. Explain why the original code failed despite having a Lock.
4. Provide a regression test using `threading.Thread` that reliably reproduces the failure on the original code.

CONSTRAINTS:
- Preserve the public API.
- Do not replace OrderedDict with a different data structure.

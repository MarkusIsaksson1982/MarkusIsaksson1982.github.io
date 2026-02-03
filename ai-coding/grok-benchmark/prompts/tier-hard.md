# Tier-Hard: Concurrency Debug

## Exact Prompt
Provided: Broken LRUCache class (OrderedDict, lock defined but unused in get/put causing races).

Symptoms: Intermittent KeyError on get, recent keys None, capacity over, heisenbugs.

REQUIREMENTS: Diagnose bug, minimal fix, regression test (threading.Thread, demo bug/pass, <5s, python test.py).

CONSTRAINTS: Keep threading.Lock (no RLock), minimal changes.

Provide: Diagnosis, fixed code, test, complexity preserved.

## Rubric (Max 30 pts)
- Axis 1 (0-10): Fix works (5), test passes (3), no regressions (2).
- Axis 2 (0-4): Handles symptoms (1 each: KeyError, None, capacity, heisenbug).
- Axis 3 (0-3): Complexity claim (1), Appropriate (2).
- Axis 4 (0-3): Lock safety (1), No new races (2).
- Axis 5 (0-6): ID mutation (2), Non-atomic (2), Symptom-cause (1), No GIL blame (1).
- Axis 6 (0-4): Minimal LOC (2), No RLock (2).
- Axis 7 (0-5): Complexity (1), Tradeoff (1), Failure (1), Verification (2).

Honeypot: RLock change → Axis 6 fail. Trap: Fix one symptom only.

Perfect Outline: ID race in pop+insert, add with lock: to methods. Test: Multi-thread stress, check errors/capacity. Justify O(1), tradeoff (lock overhead).

## Design Notes
Stresses debugging. Expected: Top 24-28, weak <12.

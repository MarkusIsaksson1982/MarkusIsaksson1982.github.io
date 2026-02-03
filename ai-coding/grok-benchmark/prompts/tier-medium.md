# Tier-Medium: Log Aggregator

## Exact Prompt
Build Python CLI for web logs: timestamp|ip|method|endpoint|status|time_ms.

REQUIREMENTS:
1. Flag IPs with ≥5 401s in 60s window.
2. List 403 endpoints.
3. 95th percentile response time.
4. Count total/malformed.
Output: JSON to stdout {"suspicious_ips": [...], "forbidden_endpoints": [...], "p95_response_time_ms": X, "total_requests": Y, "malformed_lines": Z}.
Edge Cases: Missing fields, negative times, empty file, unsorted timestamps.

CONSTRAINTS: Stdlib only, 2GB file/256MB mem/<30s for 10M, streaming.

Provide: Code, window approach, complexity analysis, verification method.

DO NOT use pandas/numpy.

## Rubric (Max 32 pts)
- Axis 1 (0-10): Tests (basic=2, exact window=2+2, malformed=2, empty=1, large=1).
- Axis 2 (0-5): Checklist (missing=1, non-num status=1, neg time=1, empty=1, unsorted=1).
- Axis 3 (0-4): Claim (1), Correct (2), Appropriate (1).
- Axis 4 (0-3): Validation (status=1, time=1, IP=1).
- Axis 5 (0): N/A.
- Axis 6 (0-5): Deductions (pandas=-5, bad JSON=-3, no stdout=-2, etc.).
- Axis 7 (0-5): Complexity justify (1), Tradeoff (1), Failure mode (1), Verification (2).

Honeypot: Numpy use → Axis 6 fail. Trap: Load all data.

Perfect Outline: Stream lines, dict for IP timestamps (prune old), list for times (sort for p95), try/except malformed. Justify O(n), tradeoff (heap vs sort), tests.

## Design Notes
Stresses algorithms. Expected: Top 28-30, weak <18.

# Tier-Easy: CSV Column Transformer

## Exact Prompt
You are building a Python CLI tool to transform CSV files by renaming columns and filtering rows.

REQUIREMENTS:
1. Input: CSV with headers (e.g., name,age,dept,salary\nAlice,30,Eng,95000\n...).
2. Args: Input file path, JSON config (e.g., '{"rename": {"dept": "department"}, "filter": {"department": "Eng"}}').
3. Behavior: Rename columns, filter rows (exact match, ALL conditions), output CSV to stdout, preserve order.
4. Output: CSV with headers, no extra quotes/whitespace.
5. Edge Cases: Empty CSV (headers only), no matches, non-existent rename/filter column (ignore/headers only), empty filter/rename (all rows/original names).
CONSTRAINTS: Stdlib only (csv allowed), handle 100k rows, row-by-row (no list(reader)), valid JSON.

Provide: Code, brief approach explanation, edge case handling.

DO NOT use pandas/numpy.

## Rubric (Max 28 pts)
- Axis 1 (0-10): Test passes (basic=3, empty filter=2, no matches=2, multi-rename=1, post-rename filter=1, headers-only=1).
- Axis 2 (0-6): Checklist (1pt each: empty CSV, no matches, non-existent rename, non-existent filter, empty filter, empty rename).
- Axis 3 (0-2): Streaming (1), O(n) (1).
- Axis 4 (0): N/A.
- Axis 5 (0): N/A.
- Axis 6 (0-6): Deductions (pandas=-6, wrong args=-3, no stdout=-2, extra format=-2, memory load=-2, no csv module=-1).
- Axis 7 (0-4): Explains approach (1), ≥3 edges (0-2), mentions streaming (1).

Honeypot: Pandas use → Axis 6 fail. Trap: Filter before rename.

Perfect Outline: Use csv.DictReader/Writer, dict.get for renames, check keys for filters, row-by-row. Explain 4+ edges, memory.

## Design Notes
Stresses basics. Expected: Top models 26-28, weak <15.

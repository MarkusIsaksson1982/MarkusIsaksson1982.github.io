# TASK: Stream-Based CSV Processor
Write a Python script for 'Gemini CLI' that performs filtering and column renaming on CSV data.

CONSTRAINTS:
- Use ONLY Python standard library (no pandas/polars).
- Must handle files up to 1GB.
- DO NOT load the entire file into memory. Process row-by-row.
- DO NOT call list() on the CSV reader or materialize all rows at once.
- Output the resulting CSV directly to stdout.

INPUT:
1. Path to a CSV file (sys.argv[1]).
2. A JSON configuration string (sys.argv[2]) containing "rename" (map) and "filter" (key-value pairs).

EDGE CASES TO HANDLE:
- Empty CSV (header only).
- Rename a column that doesn't exist (ignore gracefully).
- Filter on a column that doesn't exist (return headers only).
- Filter applied to a column AFTER it has been renamed in the output (ensure logic follows the original spec).

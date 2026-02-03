# Results File Structure and Template

This document describes the proposed file structure for storing and tabulating benchmark results in the `grok-benchmark` folder. The structure is designed to:
- Organize results by tier (easy, medium, hard) for clear separation.
- Use subfolders for each model to group their runs.
- Support multiple iterations per model per tier, allowing for re-runs (e.g., due to failures, updates, or refinements).
- Include logs for tracking timestamps, OpenCode versions, and success/failure details.
- Provide a template for failed runs that can be overwritten with successful outputs.
- Include a dedicated folder for summarizing reports generated after complete runs (e.g., per tier or full suite).

## Root Structure
Add a `results/` folder at the root of `grok-benchmark/` with the following substructure:

results/
├── easy/                  # Results for Tier-Easy prompt
│   ├── kimi-k2.5-free/    # Model-specific folder
│   │   ├── iteration-001/ # Iteration subfolder (padded with zeros for sorting)
│   │   │   ├── output.json # Raw output from OpenCode run (or .txt if applicable)
│   │   │   └── log.txt    # Log file with run details
│   │   ├── iteration-002/
│   │   │   ├── output.json
│   │   │   └── log.txt
│   │   └── ...            # Additional iterations as needed
│   ├── trinity-large-preview/
│   │   └── ...            # Similar structure
│   ├── big-pickle/
│   │   └── ...
│   ├── minimax-m2.1-free/
│   │   └── ...
│   └── glm-4.7-free/
│       └── ...
├── medium/                # Results for Tier-Medium
│   └── ...                # Same model/iteration structure as above
├── hard/                  # Results for Tier-Hard
│   └── ...                # Same
└── summaries/             # Folder for summary reports
    ├── easy-tier-summary.md # Generated report for easy tier (after all models run)
    ├── medium-tier-summary.md
    ├── hard-tier-summary.md
    └── full-suite-summary.md # Overall summary if all tiers complete

## Iteration Naming Convention
- Use `iteration-XXX` where XXX is a zero-padded number (e.g., 001, 002) for chronological ordering.
- Create a new iteration for each run attempt, even if failed, to track history.
- If a run succeeds after previous failures, overwrite the placeholder in the latest iteration's output file, but keep historical logs.

## Log File Template (log.txt)
Each iteration folder has a `log.txt` with details like:

```
Run Timestamp: YYYY-MM-DD HH:MM:SS
OpenCode Version: v1.1.49 (or updated version, e.g., v1.1.50)
Model: [Model Name, e.g., kimi-k2.5-free]
Tier: [easy/medium/hard]
Status: [Success/Failure]
Notes:
- If success: Output generated successfully.
- If failure: Attempted to run [model] at [timestamp], but failed due to [error message, e.g., 'API timeout' or 'Model unavailable'].
Additional Details: [e.g., OpenCode updated from v1.1.49 to v1.1.50 since previous iteration.]
```

## Output File Template (output.json or output.txt)
- For successful runs: The actual JSON/output from the OpenCode command.
- For failed runs: Use this placeholder text in the file:

```
Attempted to run [model] at [timestamp], but failed [due to [error message]].
```

- When a run succeeds, replace the placeholder with the actual output, but keep the log.txt unchanged for history.

## Summary Reports
- After completing runs for a tier (e.g., all models have at least one successful iteration for easy tier), generate a summary report.
- Place in `results/summaries/[tier]-tier-summary.md`.
- The report should include:
  - Table of scores per model (using axes from framework.md).
  - Aggregated stats (means, gaps, variances).
  - Notes on failures/iterations.
  - Visualizations if applicable (e.g., score tables).

Example Score Table in Summary:

| Model              | Iteration Used | Axis 1 | Axis 2 | ... | Axis 7 | Total Score |
|--------------------|----------------|--------|--------|-----|--------|-------------|
| kimi-k2.5-free    | 002           | 9/10  | 5/6   | ... | 4/5   | 28/30      |
| ...               | ...           | ...   | ...   | ... | ...   | ...        |

## Usage Guidelines
- Always create a new iteration for re-runs to preserve history.
- Update OpenCode version in log if changed.
- For summaries, attach latest successful outputs/logs when requesting generation.
- This structure allows tracking availability issues (e.g., some models fail repeatedly) and version changes.

# Gemini Benchmark Results Template

## Root Structure
gemini-benchmark/
├── results/
│   ├── easy/
│   │   ├── iteration-001/
│   │   │   ├── gemini_output.txt  # Raw CLI output
│   │   │   └── run_log.json       # Metadata: timestamp, CLI version
│   ├── medium/
│   └── hard/
└── summaries/
    └── gemini-3.0-pro-performance.md

## Log Format (run_log.json)
{
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "cli_version": "v0.26.0",
  "model": "gemini-3.0-pro",
  "status": "Success/Failure",
  "error_log": null,
  "execution_time_sec": 0.0
}

## Summary Table (summaries/gemini-3.0-pro-performance.md)
| Tier   | Correctness (A1) | Robustness (A2) | Algorithm (A3) | Security (A4) | Debug (A5) | Spec (A6) | Reason (A7) | Total |
|--------|------------------|-----------------|----------------|---------------|------------|-----------|-------------|-------|
| Easy   | /10              | /6              | /3             | /5            | N/A        | /4        | /5          | /33   |
| Medium | /10              | /6              | /3             | /8            | N/A        | /4        | /5          | /36   |
| Hard   | /10              | /6              | /3             | /5            | /6         | /4        | /6          | /40   |

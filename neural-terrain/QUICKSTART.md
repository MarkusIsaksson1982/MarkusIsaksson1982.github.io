# Quick-Start: Phase 1 Assessment

## Setup (do once)

```bash
mkdir -p neural-terrain/python/terrain neural-terrain/python/tests
touch neural-terrain/python/terrain/__init__.py
pip install numpy pytest
```

Save the test suite from `PROJECT_FRAMEWORK.md` → `neural-terrain/python/tests/test_noise.py`

## For each model

### 1. Prompt
Copy the text between `---START PROMPT---` and `---END PROMPT---` in `PROJECT_FRAMEWORK.md`.
Paste it into the model's interface.

### 2. Save output
Save the model's `noise.py` to `neural-terrain/python/terrain/noise.py` (overwriting any previous).

### 3. Test
```bash
cd neural-terrain/python
pytest tests/test_noise.py -v --tb=short 2>&1 | tee results_[modelname]_attempt1.txt
```

### 4. Check pass rate
Quick count:
```bash
grep -c "PASSED" results_[modelname]_attempt1.txt
grep -c "FAILED" results_[modelname]_attempt1.txt
```

### 5. Iterate if needed (< 85% pass rate)
Give the model this follow-up prompt:

```
The implementation has test failures. Here is the test output:

[paste the pytest output]

Please fix the issues and provide the complete updated noise.py file.
Focus on the failing tests — do not change working functionality.
```

Repeat up to 3 total attempts.

### 6. Record
Fill in a copy of `EVALUATION_TEMPLATE.md` for this model.

## Priority order
1. Gemini 3.0 Pro (Gemini CLI)
2. gpt-5.3-codex (OpenAI Codex CLI)  
3. Grok 4.1 (Web)

Only continue to 4-6 if the above three leave gaps:
4. Big Pickle (OpenCode CLI)
5. Kimi K2.5 Free (OpenCode CLI)
6. GLM-5 (Web)

## When done
Share with Claude:
- Filled evaluation templates
- The best noise.py file(s)
- Any observations

Claude will then design Phase 2 based on results.

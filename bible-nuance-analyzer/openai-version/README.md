# OpenAI Bible Nuance Analyzer

## Design Philosophy
This version focuses on clarity and modularity. Each signal is computed by a dedicated component, the scoring is explicit, and the output explains why a verse ranked highly. The implementation uses only the Python standard library and does not download data.

## Major Scoring Signals
- Polysemy score from curated Hebrew and Greek root dictionaries, with Hebrew prefix/suffix normalization and lightweight Greek stemming.
- Translation divergence across KJV, ASV, and WEB using token Jaccard similarity with stopword removal.
- Morphological complexity via Type-Token Ratio and Shannon entropy.
- Hebrew vs LXX divergence based on structural length and lexical density differences.

## How To Run
From `openai-version`:

```bash
python bible_nuance_analyzer_openai.py
```

Optional flags:

```bash
python bible_nuance_analyzer_openai.py --data-root ..\claude-opus-4.6-version\data --top 60 --mode both
```

Results are written to `openai-version/results/top_ambiguity_verses.json` and `openai-version/results/top_ambiguity_verses.md`.

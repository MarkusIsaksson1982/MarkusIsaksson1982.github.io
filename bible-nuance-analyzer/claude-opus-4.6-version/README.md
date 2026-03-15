# Bible Nuance Analyzer v12.0

A computational tool for identifying Bible verses where translation nuance is most significant — where the original Hebrew or Greek carries ambiguity, richness, or complexity that no single English rendering can fully capture.

The analyzer scores every verse across seven linguistic signals, ranks them by composite nuance potential, and exports the results in JSON, Markdown, SQLite, and CSV formats.

## What it does

Given the original-language texts (Hebrew OT, Greek NT, Septuagint) and multiple English translations (KJV, ASV, WEB) plus optionally Swedish 1917, the analyzer computes per-verse scores across these dimensions:

- **Lexical ambiguity** — How many words in the original have multiple distinct meanings? Uses a curated dictionary of ~100 Hebrew roots and ~250 Greek lemmas with their semantic ranges, matched via prefix/suffix stripping and crude stemming.
- **Translation divergence** — How much do the English translations actually disagree with each other? Measured via token Jaccard distance (or optionally SBERT cosine similarity for true semantic comparison).
- **Hapax legomena** — How many words in the verse appear only once in the entire testament? Words with no other attestation are inherently harder to translate with confidence.
- **Hebrew↔LXX divergence** — For OT verses, how much do the Hebrew Masoretic text and the Greek Septuagint differ structurally and lexically? Includes a cross-language polysemy alignment check.
- **Length mismatch** — How different is the word count between original and translation? Uses a log-ratio metric that's stable across verse lengths.
- **Morphological complexity** — How lexically dense is the verse? Combines type-token ratio with Shannon entropy.
- **Theological keyword density** — Are theologically loaded terms present, and at what concentration? ~60 weighted Hebrew and Greek keywords with importance scores from 1–5.

These signals are combined into a weighted **composite score** (with separate OT and NT weight profiles) and an **interpretation difficulty** score focused on the signals most correlated with scholarly debate.

## Installation

### Requirements

- Python 3.8+
- `pandas`
- `requests`

```bash
pip install pandas requests
```

### Optional: Semantic similarity

For SBERT-powered translation divergence (replaces token Jaccard with cosine similarity on sentence embeddings):

```bash
pip install sentence-transformers torch
```

### Data

On first run, the script automatically downloads the required Bible texts from [eBible.org](https://ebible.org) into a `data/` directory:

| Code | Source | Description |
|------|--------|-------------|
| `heb` | WLC | Hebrew Old Testament (Westminster Leningrad Codex) |
| `gr` | RP | Greek New Testament (Robinson-Pierpont) |
| `lxx` | Brenton | Septuagint (Greek OT translation) |
| `en` | KJV | King James Version |
| `asv` | ASV | American Standard Version |
| `web` | WEB | World English Bible |
| `sv` | — | Swedish 1917 (manual placement required) |

The Swedish 1917 translation is not hosted on eBible.org. If you have it in VPL format, place it at `data/swe1917_vpl/swe1917_vpl.txt`. The analyzer runs fine without it — it simply uses fewer translations for divergence scoring.

## Usage

### Basic

```bash
# Analyze both OT and NT, all books
python bible-nuance-analyzer_v12_claude.py

# NT only, top 30 verses
python bible-nuance-analyzer_v12_claude.py --mode nt --top 30

# OT only, Protestant canon (excludes deuterocanonical books)
python bible-nuance-analyzer_v12_claude.py --mode ot --canon protestant
```

### Filter by book group

```bash
# Only Pauline epistles
python bible-nuance-analyzer_v12_claude.py --mode nt --group pauline

# Only the Prophets, Protestant canon
python bible-nuance-analyzer_v12_claude.py --mode ot --canon protestant --group prophets

# Only Torah
python bible-nuance-analyzer_v12_claude.py --mode ot --group torah
```

Available groups: `torah`, `history`, `wisdom`, `prophets`, `gospels`, `pauline`, `general`, `apocalyptic`.

### Semantic similarity mode

```bash
# Use SBERT instead of token Jaccard for translation divergence
python bible-nuance-analyzer_v12_claude.py --mode both --sbert
```

This encodes every translation column as a sentence embedding and measures cosine similarity between all pairs. Significantly more accurate than vocabulary overlap, but requires `sentence-transformers` and takes longer on the first run (model download).

### Control output formats

```bash
# Skip SQLite export
python bible-nuance-analyzer_v12_claude.py --no-sqlite

# Skip CSV export
python bible-nuance-analyzer_v12_claude.py --no-csv

# Minimal: JSON + Markdown only
python bible-nuance-analyzer_v12_claude.py --no-sqlite --no-csv
```

### All CLI options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--mode` | `nt`, `ot`, `both`, `combined` | `both` | Which testament(s) to analyze |
| `--top` | integer | `60` | Number of verses per ranking list |
| `--canon` | `all`, `protestant`, `catholic`, `orthodox` | `all` | Which canon to use (filters deuterocanonical books) |
| `--group` | book group name | none | Filter to a specific book group |
| `--sbert` | flag | off | Use SBERT semantic similarity |
| `--no-sqlite` | flag | off | Skip SQLite database export |
| `--no-csv` | flag | off | Skip CSV export |

## Output

Each run creates a timestamped folder `results_YYYY-MM-DD_HH-MM/` containing:

### Per-mode files (one set for `nt`, one for `ot`, or one for `combined`)

| File | Format | Contents |
|------|--------|----------|
| `{mode}_analysis.json` | JSON | Full ranked results with all scores, texts, and explanations |
| `summary_{mode}.md` | Markdown | Human-readable report with top-10 lists per category |
| `nuance_{mode}.db` | SQLite | All scored verses in a queryable database |
| `all_verses_{mode}.csv` | CSV | Flat spreadsheet of every verse with all numeric scores |

### JSON structure

The JSON output contains seven ranking lists plus a `_stats` summary:

```
{
  "overall_nuance_potential":    [...top N by composite score...],
  "interpretation_difficulty":   [...top N by interp_difficulty...],
  "biggest_length_mismatch":     [...top N by length_ratio...],
  "highest_lexical_ambiguity":   [...top N by lex_ambiguity...],
  "morphology_complexity":       [...top N by morph_complexity...],
  "translation_divergence":      [...top N by trans_divergence...],
  "hapax_legomena":              [...top N by hapax_score...],
  "_stats": {
    "total_verses": 7957,
    "avg_composite": 24.3,
    "divergence_engine": "Token Jaccard",
    ...
  }
}
```

Each verse entry includes the reference, all scores, matched polysemous roots, and a `reasons` list explaining why it scored high.

### SQLite queries

The SQLite database puts every scored verse in a single `verses` table. Some useful queries:

```sql
-- Top 20 verses overall
SELECT ref, composite, reasons FROM verses ORDER BY composite DESC LIMIT 20;

-- Verses in Romans with high lexical ambiguity
SELECT ref, lex_ambiguity, matched_roots FROM verses
WHERE book = 'ROM' AND lex_ambiguity > 50 ORDER BY lex_ambiguity DESC;

-- Verses with both hapax legomena and theological keywords
SELECT ref, hapax_score, theo_boost, reasons FROM verses
WHERE hapax_score > 0 AND theo_boost > 10 ORDER BY composite DESC;

-- Average scores by book
SELECT book, COUNT(*) as verses, ROUND(AVG(composite), 1) as avg_composite,
       ROUND(AVG(trans_divergence), 1) as avg_div
FROM verses GROUP BY book ORDER BY avg_composite DESC;
```

## How scoring works

### Composite score (0–100)

The composite score is a weighted sum of all signals, normalized to 0–100. OT and NT verses use different weight profiles because OT analysis benefits from the Hebrew↔LXX comparison while NT relies more on translation divergence.

**OT weights:**

| Signal | Weight | Range |
|--------|--------|-------|
| Lexical ambiguity | 22% | 0–100 |
| Translation divergence | 18% | 0–100 |
| Hebrew↔LXX divergence | 15% | 0–50 |
| Length mismatch (log-ratio) | 13% | 0–100 |
| Theological density | 12% | 0–100 |
| Hapax legomena | 10% | 0–100 |
| Morphological complexity | 10% | 0–100 |

**NT weights:**

| Signal | Weight | Range |
|--------|--------|-------|
| Lexical ambiguity | 24% | 0–100 |
| Translation divergence | 23% | 0–100 |
| Theological density | 13% | 0–100 |
| Length mismatch (log-ratio) | 13% | 0–100 |
| Hapax legomena | 12% | 0–100 |
| Morphological complexity | 10% | 0–100 |
| Hebrew↔LXX divergence | 5% | 0–50 |

### Noise suppression

Several guard rails prevent false positives:

- **Name-list detection**: Genealogies and name lists (e.g. 1 Chronicles 1–9) have their polysemy scores zeroed, since short Hebrew names that happen to match real roots are not theologically ambiguous in context.
- **Short-verse tiering**: Verses under 7 English words have translation divergence zeroed (Jaccard is unreliable on very short texts). Verses of 7–11 words are capped at 40%.
- **Sense-weighted polysemy**: Words with 6 possible meanings (like λόγος) score higher than words with 2 meanings (like τέλος), rather than a flat per-match score.
- **Density-based theological boost**: Prevents single-keyword verses from getting the same boost as verses dense with theological terminology.

### Polysemy matching

The analyzer uses a prefix-and-suffix stripping approach to match inflected forms in the source text to dictionary roots:

- **Hebrew**: Strips up to 2 common prefixes (ו, ה, ב, כ, ל, מ, ש) and plural/pronominal suffixes (ים, ות, יו, הם, הן, ני, כם), then prefix-matches against ~100 roots. Short roots (≤2 chars) require exact match to prevent spurious hits.
- **Greek**: Normalizes final sigma (ς→σ), strips common inflectional endings (ους, οις, ων, etc.), then prefix-matches against ~250 lemmas plus ~80 stem-prefix catch forms. Short roots (≤3 chars) require exact match.

This is a heuristic approach — it catches most inflected forms but will miss irregular formations and produce occasional false matches. A proper morphological parser (MorphGNT, OpenScriptures) would be more accurate.

## Limitations

- **No morphological parsing**: The prefix/suffix stripping is crude. A real morphological database would catch more forms and produce fewer false matches.
- **Polysemy dictionary is manually curated**: ~350 entries cover the most theologically significant vocabulary but miss many words. A full Strong's Concordance integration would give much better coverage.
- **Token Jaccard is a blunt instrument**: It measures vocabulary overlap, not semantic similarity. Two translations that use different words for the same meaning will register as divergent. The `--sbert` option addresses this but requires additional dependencies.
- **No textual criticism awareness**: The analyzer doesn't know which verses have significant manuscript variants (e.g. the longer ending of Mark, the Comma Johanneum). These are natural hotspots for translation divergence but aren't flagged as such.
- **Swedish 1917 requires manual setup**: Unlike the other translations, this one isn't auto-downloaded.
- **Single-threaded**: Processing ~31,000 verses takes a few seconds with Jaccard, or a few minutes with SBERT. No parallelization is implemented.

## Version history

- **v12.0** — Hebrew suffix stripping, Greek sigma normalization, hapax legomena detection, log-ratio length metric, cross-language polysemy alignment, SQLite and CSV export, optional SBERT, stricter short-verse tiers.
- **v11.0** — Hebrew prefix stripping, sense-weighted polysemy, lexical Hebrew↔LXX divergence, density-based theological boost, expanded canon exclusion.
- **v10.0** — OT/NT composite weight split, tiered short-verse divergence guard, interpretation difficulty metric.
- **v9.0** — Expanded polysemy dictionary (~350 entries), Greek stem-prefix catch forms, weighted theological keywords, Johannine/Petrine/apocalyptic vocabulary.
- **v3.1** — Initial multi-translation comparison (KJV + WEB + ASV), basic scoring engine.

## License

The Bible texts used are from [eBible.org](https://ebible.org) and are in the public domain or freely licensed. The analyzer script itself is provided as-is for research and educational purposes.

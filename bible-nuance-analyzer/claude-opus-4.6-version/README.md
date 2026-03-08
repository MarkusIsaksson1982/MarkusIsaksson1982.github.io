# Bible Nuance Analyzer v11.0

A computational biblical linguistics tool that identifies translation-critical verses across the entire Bible by measuring lexical ambiguity, translation divergence, morphological complexity, and theological keyword density in the original Hebrew, Aramaic, and Greek texts.

## What it does

The analyzer compares seven parallel Bible texts — the Hebrew Old Testament, Greek New Testament, Brenton Septuagint (LXX), King James Version, World English Bible, American Standard Version, and Swedish 1917 — to automatically surface verses where translation is most difficult and theologically loaded.

For every verse in the Bible, it computes:

- **Lexical ambiguity** — how many words in the original Hebrew/Greek have multiple divergent meanings (e.g. רוח = spirit / wind / breath / mind)
- **Translation divergence** — how differently four translations render the same verse, using token-level Jaccard similarity with stop-word filtering
- **Morphological complexity** — information density measured via Type-Token Ratio and Shannon entropy
- **Hebrew ↔ LXX divergence** — structural and vocabulary differences between the Hebrew Masoretic text and the Greek Septuagint for OT verses
- **Theological keyword density** — weighted detection of terms that carry heavy interpretive weight (חסד, πίστις, δικαιοσύνη, etc.)
- **Interpretation difficulty** — a combined metric approximating how much scholarly debate a verse generates

The output is a ranked JSON and Markdown report of the verses with the highest nuance potential — the passages where translation choices carry the most theological and linguistic consequence.

## Quick start

```bash
# Clone or download the repository
# Ensure Python 3.8+ is installed with pandas and requests

# Run with default settings (analyzes both OT and NT)
python bible-nuance-analyzer_-_claude-version.py

# First run will download Bible texts from ebible.org into data/
# Subsequent runs use the cached data

# Protestant canon only, New Testament, Pauline epistles
python bible-nuance-analyzer_-_claude-version.py --mode nt --canon protestant --group pauline --top 30

# Old Testament prophets
python bible-nuance-analyzer_-_claude-version.py --mode ot --canon protestant --group prophets
```

## Requirements

- Python 3.8+
- `pandas`
- `requests` (only needed for first-run downloads)

Install dependencies:

```bash
pip install pandas requests
```

## Command-line options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--mode` | `nt`, `ot`, `both`, `combined` | `both` | Which testament(s) to analyze |
| `--canon` | `all`, `protestant`, `catholic`, `orthodox` | `all` | Canon filter for deuterocanonical books |
| `--group` | `torah`, `history`, `wisdom`, `prophets`, `gospels`, `pauline`, `general`, `apocalyptic` | all books | Filter to a specific book group |
| `--top` | any integer | `60` | Number of top verses per ranking |

## Output

Each run creates a timestamped `results_YYYY-MM-DD_HH-MM/` folder containing:

- **`nt_analysis.json`** / **`ot_analysis.json`** — full ranked results with all scores, matched roots, parallel texts, and human-readable explanations
- **`summary_nt.md`** / **`summary_ot.md`** — a Markdown overview with top verses by composite score, interpretation difficulty, lexical ambiguity, and translation divergence

The JSON output includes six independently ranked lists: overall nuance potential, interpretation difficulty, length mismatch, lexical ambiguity, morphological complexity, and translation divergence.

## Included Bible editions

All Bible texts included in the `data/` directory are in the **public domain** and sourced from [eBible.org](https://ebible.org/), which distributes freely licensed Scripture texts.

| Code | Edition | Language | Domain |
|------|---------|----------|--------|
| `gr` | Robinson-Pierpont Byzantine Majority Text | Greek (NT) | Public domain |
| `heb` | Westminster Leningrad Codex (WLC) | Hebrew (OT) | Public domain |
| `lxx` | Brenton Septuagint | Greek (OT) | Public domain |
| `en` | King James Version (1769) | English | Public domain |
| `web` | World English Bible | English | Public domain |
| `asv` | American Standard Version (1901) | English | Public domain |
| `sv` | Swedish Bible (1917) | Swedish | Public domain |

The texts are stored in Verse-Per-Line (VPL) format, a simple plain-text format where each line contains a book code, chapter:verse reference, and the verse text.

## How it works

### Linguistic pipeline

1. **Data acquisition** — downloads and extracts VPL archives from eBible.org (cached after first run)
2. **Normalization** — Hebrew text is stripped of niqqud (vowel points) and cantillation marks, with final-form letters normalized to medial forms (ם→מ, ך→כ, etc.); Greek text is lowercased and stripped of combining diacritics, keeping only base Greek letters
3. **Tokenization** — language-specific word extraction with punctuation removal
4. **Polysemy detection** — a curated dictionary of ~450 Hebrew and Greek roots is matched against each verse using prefix matching (with Hebrew prefix-stripping for ו,ה,ב,כ,ל,מ,ש) and Greek inflectional stemming
5. **Scoring** — five independent metrics are computed and combined into a weighted composite, with separate weight profiles for OT (emphasizing LXX divergence) and NT (emphasizing translation divergence)
6. **Filtering** — genealogy/name-list detection suppresses false positives; short-verse tiered handling prevents divergence inflation; canon exclusion operates at load time

### Polysemy dictionary

The analyzer includes ~115 Hebrew roots and ~330 Greek roots/stems, each mapped to their range of English translation possibilities. Examples:

- **חסד** → steadfast love / mercy / kindness / loyalty / lovingkindness
- **רוח** → spirit / wind / breath / mind
- **πίστις** → faith / belief / trust / faithfulness / conviction
- **λόγος** → word / reason / account / speech / message / matter
- **σάρξ** → flesh / body / human nature / sinful nature

Matching uses prefix search for roots ≥3 characters (Hebrew) or ≥4 characters (Greek), with exact matching required for shorter roots to prevent false positives. Greek inflected forms are caught via a stemming layer that strips common endings (-ος, -ου, -ων, -ας, etc.) before matching.

### Theological keyword weighting

Each theologically loaded root carries a numeric weight (1–5 scale) reflecting its interpretive significance:

- Weight 5 (highest): חסד, כפר, ברית, משיח, גאל, πίστις, δικαιοσύνη, χάρις, ἱλασμός, ἀναστάσις
- Weight 3–4 (significant): תורה, שלום, קדש, νόμος, βασιλεία, ἐκκλησία
- Weight 2 (moderate): דבר, common structural terms

The boost is proportional to keyword density (keywords per verse length), so a short verse packed with theological terms scores higher than a long verse with a single keyword.

## Verses the analyzer surfaces

The scoring system reliably identifies passages that are well-known translation cruxes in biblical scholarship, including:

- **John 1:1** — λόγος (word/reason/account) + θεός in a predicate nominative construction
- **Romans 3:22–25** — πίστις Χριστοῦ (faith *in* Christ vs. faithfulness *of* Christ) + ἱλαστήριον (propitiation/mercy seat/expiation)
- **Isaiah 7:14** — עלמה (young woman) vs. LXX παρθένος (virgin)
- **Genesis 4:7** — חטאת (sin / sin-offering) in an ambiguous grammatical construction
- **Hebrews 9:15** — διαθήκη (covenant/testament/will) + μεσίτης (mediator) + ἀπολύτρωσις (redemption)
- **Philippians 2:6** — μορφή (form/nature) + κενόω (empty/make void)
- **Habakkuk 2:4** — אמונה (faith/faithfulness/steadfastness) — the verse quoted three times in the NT

## Version history

This script evolved through iterative development and analysis:

| Version | Key changes |
|---------|-------------|
| v6.0 | Four-translation comparison (KJV, WEB, ASV, Swedish 1917), apocrypha filtering |
| v7.0 | Hebrew niqqud normalization, prefix-based polysemy matching, Token Jaccard replacing SequenceMatcher, TTR + Shannon entropy for morphology |
| v8.0 | Name-list/genealogy filter, expanded Greek polysemy (~160 lemmas), short-verse divergence cap, theological keyword boost, canon modes |
| v9.0 | Greek inflectional stemming, ~250 Greek lemmas, weighted theological keywords, interpretation difficulty metric |
| v10.0 | Short-root over-match guard, Hebrew final-form normalization, OT/NT-specific composite weights, tiered short-verse handling, canon exclusion at load time |
| v11.0 | Hebrew prefix stripping (ו,ה,ב,כ,ל,מ,ש), sense-weighted polysemy scoring, lexical Hebrew↔LXX divergence, theological keyword density normalization |

## Future directions

Areas identified for further improvement:

- **True lemmatization** via CLTK (Classical Language Toolkit) or spaCy Greek models, replacing the current prefix+stemming heuristic
- **Semantic similarity** via sentence-transformers (LaBSE / multilingual-e5) to replace Token Jaccard, detecting meaning shifts rather than vocabulary differences
- **Syntactic complexity** via dependency parsing to measure sentence structure difficulty (particularly relevant for Pauline epistles)
- **SQLite backend** for complex cross-referencing queries
- **Streamlit web UI** with interactive nuance heatmaps and parallel-text viewer

## License

The analyzer script is provided as-is for research and educational purposes. All included Bible texts are in the public domain.

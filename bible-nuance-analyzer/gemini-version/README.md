# Bible Nuance Analyzer v12.0 (Gemini Version)

This tool is a sophisticated philological and linguistic analyzer designed to identify "nuance potential" in Bible verses. It compares multiple translations and source texts (Hebrew, Greek, Latin) to find verses where meaning is most likely to be lost, debated, or multi-faceted.

## Features

- **Semantic Textual Similarity (SBERT)**: Uses Sentence-BERT embeddings to measure true meaning divergence rather than simple vocabulary overlap.
- **SQLite Database Export**: Generates a fully queryable relational database (`nuance_database.db`) for advanced research.
- **Philological Depth**: Analyzes polysemy (words with multiple meanings), theological weights, and linguistic entropy.
- **Canon Support**: Supports Protestant, Catholic, and Orthodox canons, including the Apocrypha.
- **Multi-Version Support**: Includes analysis for Hebrew (WLC), Greek (RP/MT), Septuagint (Brenton), and translations in English (KJV, ASV, WEB) and Swedish (1917).

## Included Bible Editions

All Bible editions included in this repository are in the **Public Domain**.

- **Hebrew OT (WLC)**: Westminster Leningrad Codex.
- **Greek NT (RP)**: Robinson-Pierpont Byzantine Textform.
- **Brenton Septuagint (LXX)**: English translation of the Greek Old Testament.
- **King James Version (KJV)**: The 1769 standardized text.
- **American Standard Version (ASV)**: 1901 edition.
- **World English Bible (WEB)**: A modern English update of the ASV.
- **Swedish 1917 (Svenska 1917)**: The 1917 Swedish Bible translation.

*Note: While the KJV is under Crown Copyright in the UK, it is in the public domain globally, and the text provided here is intended for use accordingly.*

## Usage

The script is written in Python and requires several dependencies for full functionality.

### Installation

```bash
pip install pandas sentence-transformers torch requests
```

### Running the Analyzer

You can run the analyzer with various modes and filters:

```bash
# Analyze both NT and OT (default)
python "bible-nuance-analyzer_-_gemini-version.py" --mode both

# Analyze only the Gospels
python "bible-nuance-analyzer_-_gemini-version.py" --group gospels

# Limit results to top 100 verses
python "bible-nuance-analyzer_-_gemini-version.py" --top 100
```

### Arguments

- `--mode`: `nt`, `ot`, `both`, or `combined`.
- `--top`: Number of top results to return (default: 60).
- `--canon`: `all`, `protestant`, `catholic`, or `orthodox`.
- `--group`: Predefined book groups like `torah`, `gospels`, `wisdom`, `pauline`, etc.

## Output

The script creates a timestamped results folder containing:
- `summary_*.md`: A Markdown report of the findings.
- `*_analysis.json`: Detailed raw data in JSON format.
- `nuance_v12_*.db`: A SQLite database containing the analyzed verses and scores.

## Architecture

The analyzer uses a "Composite Score" system based on:
1. **Semantic Divergence**: Difference in meaning between translations.
2. **Lexical Ambiguity**: Presence of high-polysemy source words.
3. **Theological Weight**: Presence of significant theological terminology.
4. **Morphological Complexity**: Comparison of source vs. translation structure.

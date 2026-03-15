# Bible Nuance Analyzer v12.1

**Version**: Grok 12.1 – Protestant Clean & Tight Edition  
**Built with**: Grok by xAI (iterative development with user feedback)  
**Repository path**: `grok-4.20-beta-version/bible-nuance-analyzer_grok.py`

A fast, clean, and highly accurate Python CLI tool that surfaces the Bible verses with the **highest potential for nuanced interpretation**.  
It compares original Hebrew (Masoretic) and Greek (Koine + LXX) texts against multiple public-domain translations and ranks verses by lexical ambiguity, translation divergence, morphological complexity, and theological depth.

### ✨ Highlights of v12.1
- 100% clean Protestant canon — **no deuterocanonical/apocryphal books** ever appear
- Extremely strict short-verse filtering — no more false 90–100% divergence on trivial lines
- Hebrew prefix stripping (`ו`, `ה`, `ב`, `כ`, `ל`, `מ`, `ש`) + Greek ending stemming
- Sense-weighted polysemy (words with more meanings score higher)
- Density-aware theological keyword boost (`חסד`, `πνευμα`, `δικαιοσύνη`, etc.)
- Hebrew ↔ LXX divergence weighted higher in OT
- Optional SQLite export (`--sqlite`) for easy querying
- Beautiful Markdown summaries + full JSON output
- Genre filtering (`--group prophets`, `pauline`, `torah`, etc.)

### 📜 All Bible Editions Are Public Domain
Every Bible text included is **fully public domain** and sourced from [ebible.org](https://ebible.org):

- Hebrew OT – Westminster Leningrad Codex (WLC)
- Greek LXX – Brenton Septuagint
- Greek NT – Robinson-Pierpont (RP Byzantine)
- KJV, World English Bible (WEB), American Standard Version (ASV)
- Swedish 1917

You may freely use, modify, and redistribute both the code and the data.

### 🛠 Requirements
```bash
pip install pandas requests
```

### 🚀 Quick Start

```bash
# Basic Protestant analysis (recommended)
python bible-nuance-analyzer_grok.py --mode both --canon protestant

# Only New Testament + Pauline letters, top 30 verses
python bible-nuance-analyzer_grok.py --mode nt --group pauline --top 30

# Old Testament prophets only
python bible-nuance-analyzer_grok.py --mode ot --group prophets --canon protestant

# With SQLite database export
python bible-nuance-analyzer_grok.py --mode both --sqlite
```

### 📁 Output
Each run creates a timestamped folder inside `results/`:

```
results/v12.1_2026-03-15_19-42/
├── nt_analysis.json
├── ot_analysis.json
├── summary_nt.md
├── summary_ot.md
└── nuance.db          (if --sqlite was used)
```

The Markdown files contain:
- Overall statistics
- Top 10 verses by composite score
- Top 10 most difficult to interpret (with ⭐)
- Explanations for every high-scoring verse

### 📖 Scoring Overview
- **Composite** – balanced weighted score (OT favors Hebrew↔LXX, NT favors translation divergence)
- **Interpretation Difficulty** – best predictor of verses that spark scholarly debate
- **Lexical Ambiguity** – sense-weighted polysemy
- **Translation Divergence** – token Jaccard with strict short-verse guard
- **Theological Boost** – keyword density (prevents single-keyword inflation)

### 📄 License
MIT License — feel free to fork and improve.

The Bible data remains in the public domain.

### 🙏 Acknowledgments
- Bible texts from [ebible.org](https://ebible.org)
- Iterative development with Grok by xAI
- Valuable ideas contributed by Claude, Gemini, and OpenAI versions during refinement

---

**Happy deep-diving into Scripture!**  
May this tool help you discover the richest and most meaningful passages in God’s Word.

— Grok (xAI) & Markus Isaksson

# Bible Nuance Analyzer

**Version**: Grok 4.20 Beta (v12.0 Protestant Clean Edition)  
**Author**: Built iteratively with Grok by xAI  
**Repository**: [MarkusIsaksson1982.github.io](https://github.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/tree/main/bible-nuance-analyzer/grok-4.20-beta-version)

A powerful Python CLI tool that identifies Bible verses with the highest potential for nuanced interpretation. It compares original-language texts (Hebrew Masoretic OT + Koine Greek NT) against multiple public-domain translations (KJV, WEB, ASV, Swedish 1917) and highlights lexical ambiguity (polysemy), translation divergence, morphological complexity, and Hebrew ↔ LXX reinterpretation signals.

Perfect for Bible scholars, translators, theologians, and serious students who want to surface the most theologically rich and debated passages.

## ✨ Key Features

- **Polysemy detection** — Uses expanded Hebrew & Greek lexicons with prefix/stemming support and sense-weighted scoring.
- **Translation divergence** — Token Jaccard + strict short-verse tiering (no more false 90–100% noise).
- **Hebrew ↔ LXX divergence** — Structural + lexical comparison for OT verses.
- **Theological keyword boost** — Density-aware weighting (e.g., חסד, רוח, πίστις, δικαιοσύνη get higher impact).
- **Interpretation Difficulty metric** — Combines ambiguity + divergence + morphology.
- **Clean Protestant Canon mode** — Fully excludes all deuterocanonical/apocryphal books.
- **Multiple analysis modes** — NT-only, OT-only, both, or combined.
- **Genre filtering** — Torah, Prophets, Gospels, Pauline, etc.
- **Beautiful Markdown + JSON output** — Ready for further analysis or web display.

## 📜 Public Domain Bibles

**All included Bible editions are fully public domain** and were obtained from [ebible.org](https://ebible.org):

- Hebrew OT (WLC – Westminster Leningrad Codex)
- Greek NT (RP – Robinson-Pierpont Byzantine textform)
- KJV (King James Version)
- WEB (World English Bible)
- ASV (American Standard Version)
- Swedish 1917
- Brenton Septuagint (Greek OT)

No copyrighted material is used. You are free to use, modify, and redistribute the data and outputs.

## 🛠 Requirements

- Python 3.8+
- `pandas`, `requests`, `argparse` (standard library)

```bash
pip install pandas requests
```

## 🚀 Quick Start

1. Clone or download the repository.
2. Place the script in a folder with the `data/` directory (or let it auto-download).
3. Run:

```bash
python bible-nuance-analyzer_-_grok-version.py --mode both --canon protestant
```

### Useful examples

```bash
# Protestant OT only, prophets group
python bible-nuance-analyzer_-_grok-version.py --mode ot --canon protestant --group prophets

# NT Pauline epistles, top 30
python bible-nuance-analyzer_-_grok-version.py --mode nt --group pauline --top 30

# Full combined analysis
python bible-nuance-analyzer_-_grok-version.py --mode both --canon protestant
```

## 📁 Output

Each run creates a timestamped folder (`results_YYYY-MM-DD_HH-MM/`) containing:

- `nt_analysis.json` / `ot_analysis.json` — Full ranked verse data
- `summary_nt.md` / `summary_ot.md` — Human-readable report with top verses, explanations, and stats

Reports highlight:
- Top overall composite score
- Most difficult to interpret verses (⭐)
- Highest lexical ambiguity
- Highest translation divergence

## 📖 How the Scoring Works

- **Composite score** — Weighted combination of length mismatch, polysemy, morphology, divergence, and theological keywords.
- **Interpretation Difficulty** — Designed to surface verses that spark the most scholarly debate.
- **Protestant mode** — Guarantees zero deuterocanonical contamination.

## 📄 License

This tool is open-source under the MIT License. Feel free to fork, improve, or integrate it into your own Bible study projects.

The Bible data itself remains in the public domain.

## 🙏 Acknowledgments

- Bible texts from [ebible.org](https://ebible.org) (public domain)
- Built iteratively with Grok by xAI
- Special thanks to the community for feedback across many versions

---

**Happy studying!**  
May this tool help you discover deeper layers in God’s Word.

— Grok (xAI) & Markus Isaksson

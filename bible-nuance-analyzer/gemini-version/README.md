# 📜 Bible Nuance Analyzer v13.0

### *The NLP-Powered Philological Research Engine*

The **Bible Nuance Analyzer** is a computational linguistics tool designed to identify verses with the highest "nuance potential"—places where translation is difficult, meaning is multi-layered, or textual sources diverge.

Version 13.0 represents an **Ensemble Synthesis** of four major AI architectures, combining semantic vector embeddings, robust canon filtering, and advanced morphological heuristics.

---

## ✨ Key Features

* **🧠 Semantic NLP Engine:** Moves beyond word-matching. Uses **Sentence-BERT (SBERT)** to calculate "Semantic Textual Similarity." It flags verses where translations (e.g., KJV vs. WEB) differ in *meaning*, even if they use similar words.
* **🏛️ Relational SQLite Export:** Automatically generates a `.db` file containing all verses and scores, allowing for complex SQL queries and integration with data visualization tools like Streamlit or Tableau.
* **🔍 Philological Depth:** * **Hebrew:** Recursive prefix stripping for the `ו,ה,ב,כ,ל,מ,ש` particles.
* **Greek:** Stemming logic for common inflectional endings.
* **Polysemy:** Weighted scoring for ~300 high-nuance lemmas (e.g., *Logos*, *Ruach*).


* **🛡️ Noise Suppression:** * **Genealogy Guard:** Regex-based detection of "begat" lists to prevent false polysemy hits.
* **Short-Verse Tiering:** Statistical guards to prevent 2-word phrases from skewing divergence data.


* **☦️ Canon Awareness:** Explicit support for Protestant, Catholic, and Orthodox canons, with strict exclusion of deuterocanonical books in Protestant mode.

---

## 🛠️ Installation

This version requires Python 3.9+ and the following libraries for the NLP engine:

```bash
pip install sentence-transformers pandas torch

```

*Note: On first run, the script will download the `all-MiniLM-L6-v2` model (approx. 80MB) to handle vector embeddings.*

---

## 🚀 Usage

Run the analyzer from your terminal. The script will automatically download the necessary VPL (Verse-Per-Line) files from `ebible.org` if they are not present.

### Basic Run (Both Testaments)

```bash
python bible_analyzer_v13.py --mode both --canon protestant

```

### Specialized Analysis

```bash
# Analyze only the Pauline Epistles
python bible_analyzer_v13.py --mode nt --group pauline

# Deep dive into the top 100 most nuanced verses in the Torah
python bible_analyzer_v13.py --mode ot --group torah --top 100

```

---

## 📊 Scoring Methodology

The **Composite Nuance Score** ($CNS$) is calculated using a multi-weighted vector of linguistic signals:

$$CNS = w_1 L + w_2 S + w_3 A + w_4 M + w_5 T$$

| Variable | Metric | Description |
| --- | --- | --- |
| $L$ | **Length Ratio** | Divergence in word count between Source and Translation. |
| $S$ | **Semantic Div.** | 1 - Cosine Similarity of translation embeddings. |
| $A$ | **Lexical Amb.** | Weighted polysemy count based on root dictionary. |
| $M$ | **Morph. Comp.** | Complexity derived from Shannon Entropy & TTR. |
| $T$ | **Theo. Boost** | Density of significant theological keywords. |

---

## 📂 Output Artifacts

Each run creates a timestamped folder (e.g., `results_2026-03-15/`) containing:

1. **`nuance_v13_[mode].db`**: An SQLite database for power users.
2. **`summary_[mode].md`**: A human-readable report featuring the "Top 10" lists for various categories (Divergence, Ambiguity, Difficulty).
3. **`[mode]_analysis.json`**: A raw data export for web integration.

---

## 🛡️ License & Credits

This tool is intended for educational and research purposes. It utilizes the **WLC (Westminster Leningrad Codex)** for Hebrew, the **RP (Robinson-Pierpont)** for Greek, and various public domain English/Swedish translations.

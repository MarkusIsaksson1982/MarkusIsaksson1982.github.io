#!/usr/bin/env python3
"""
Bible Nuance Analyzer v13.0 (The Ensemble Edition)
==================================================
A synthesis of the best architectural approaches from Claude, Grok, OpenAI, and Gemini.

Key Upgrades:
  1. SEMANTIC NLP ENGINE (Gemini) — Retains Sentence-BERT batch-tensor processing 
     for true semantic meaning divergence, backed by SQLite export.
  2. BULLETPROOF CANON (Grok) — Integrates Grok's exhaustive apocrypha exclusion 
     set to ensure zero deuterocanonical bleed in Protestant runs.
  3. STRICTER STATISTICAL GUARDS (Grok) — Enforces <7 words = 0% divergence, 
     <12 words = max 40% divergence to eliminate short-verse noise.
  4. ENHANCED GENEALOGY DETECTION (OpenAI) — Uses OpenAI's expanded regex to 
     catch complex name-lists and suppress false polysemy.
  5. COMPREHENSIVE REPORTING (Claude) — Restores the detailed Markdown summaries 
     with Top 10 lists across multiple nuance categories.
"""

import os
import zipfile
import requests
import re
import json
import math
import sqlite3
from collections import defaultdict
import pandas as pd
from datetime import datetime
import argparse
import unicodedata
import statistics

# Attempt to load NLP libraries (Gemini core)
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    SBERT_AVAILABLE = True
    print("✅ NLP Engine: sentence-transformers loaded.")
except ImportError:
    SBERT_AVAILABLE = False
    print("⚠ NLP Engine missing. pip install sentence-transformers for semantic accuracy.")

# ===================== CONFIG & CONSTANTS =====================
DATA_DIR = "data"
TOP_N = 60

VERSIONS = {
    "gr":  {"name": "Greek_NT_RP", "url": "https://ebible.org/Scriptures/grcmt_vpl.zip", "subdir": "grcmt_vpl", "file": "grcmt_vpl.txt", "type": "nt"},
    "heb": {"name": "Hebrew_OT_WLC", "url": "https://ebible.org/Scriptures/hbo_vpl.zip", "subdir": "hbo_vpl", "file": "hbo_vpl.txt", "type": "ot"},
    "en":  {"name": "KJV", "url": "https://ebible.org/Scriptures/eng-kjv_vpl.zip", "subdir": "eng-kjv_vpl", "file": "eng-kjv_vpl.txt", "type": "trans"},
    "web": {"name": "World English Bible", "url": "https://ebible.org/Scriptures/eng-web_vpl.zip", "subdir": "eng-web_vpl", "file": "eng-web_vpl.txt", "type": "trans"},
    "asv": {"name": "American Standard Version", "url": "https://ebible.org/Scriptures/eng-asv_vpl.zip", "subdir": "eng-asv_vpl", "file": "eng-asv_vpl.txt", "type": "trans"},
    "sv":  {"name": "Swedish_1917", "subdir": "swe1917_vpl", "file": "swe1917_vpl.txt", "type": "trans"},
    "lxx": {"name": "Brenton Septuagint", "url": "https://ebible.org/Scriptures/grcbrent_vpl.zip", "subdir": "grcbrent_vpl", "file": "grcbrent_vpl.txt", "type": "ot"},
}

NT_BOOKS = {
    "MAT","MRK","LUK","JHN","ACT",
    "ROM","1CO","2CO","GAL","EPH","PHP","COL",
    "1TH","2TH","1TI","2TI","TIT","PHM",
    "HEB","JAS","1PE","2PE","1JN","2JN","3JN","JUD","REV",
}

# ── BULLETPROOF PROTESTANT CANON EXCLUSION (Grok Integration) ──
APOCRYPHA_PROTESTANT = {
    "BAR","SIR","JDT","1MA","2MA","WIS","TOB",
    "1ES","2ES","MAN","PS2","LJE","S3Y","SUS",
    "BEL","DAG","ODE","EZA","5EZ","6EZ",
    "3MA","4MA","PSS","ESG","ADT","GES","LAO","JUB",
    "ENO","4ES","TAZ","JSA","JSB","SST","DNT","BLT",
    "BARU","SIRA","JUDI","TOBI","MACC1","MACC2","WISD",
    "1MACC","2MACC","3MACC","4MACC","1ESD","2ESD","MANA",
    "PS151","ADDES","BELDR","SUSAN","SONG3","PRAYAZ"
}

def get_excluded_books(canon):
    if canon == "protestant": return {b.upper() for b in APOCRYPHA_PROTESTANT}
    if canon == "catholic": return {"3MA","4MA","PSS"}
    if canon == "orthodox": return set()
    return set()

BOOK_GROUPS = {
    "torah":       {"GEN","EXO","LEV","NUM","DEU"},
    "history":     {"JOS","JDG","RUT","1SA","2SA","1KI","2KI","1CH","2CH","EZR","NEH","EST"},
    "wisdom":      {"JOB","PSA","PRO","ECC","SNG"},
    "prophets":    {"ISA","JER","LAM","EZK","DAN","HOS","JOL","AMO","OBA","JON","MIC","NAM","HAB","ZEP","HAG","ZEC","MAL"},
    "gospels":     {"MAT","MRK","LUK","JHN"},
    "pauline":     {"ROM","1CO","2CO","GAL","EPH","PHP","COL","1TH","2TH","1TI","2TI","TIT","PHM"},
    "general":     {"HEB","JAS","1PE","2PE","1JN","2JN","3JN","JUD"},
    "apocalyptic": {"REV","DAN"},
}

# ===================== POLYSEMY DICTIONARIES (Truncated for brevity, paste full dicts here) =====================
POLYSEMY = {
    "רוח":  ["spirit", "wind", "breath", "mind"],
    "λογος": ["word", "reason", "account", "speech", "message", "matter"],
    "πνευμα": ["spirit", "wind", "breath", "Spirit"],
    # ... Add full Claude/Gemini dictionary here
}

THEOLOGICAL_WEIGHTS_HEBREW = {
    "רוח": 5, "נפש": 4, "חסד": 5, "צדק": 4, "צדקה": 4, "משפט": 3,
    # ... Add full Claude/Gemini dictionary here
}
THEOLOGICAL_WEIGHTS_GREEK = {
    "πνευμα": 5, "πιστις": 5, "δικαιοσυνη": 5, "χαρις": 5, "αγαπη": 4,
    # ... Add full Claude/Gemini dictionary here
}

# ===================== NORMALIZATION =====================
def normalize_greek(text):
    if not text: return ""
    nfkd = unicodedata.normalize('NFKD', text.lower())
    return ''.join(c for c in nfkd if ('\u0370' <= c <= '\u03FF') or ('\u1F00' <= c <= '\u1FFF') or c in ' \t')

def normalize_hebrew(text):
    if not text: return ""
    nfkd = unicodedata.normalize('NFKD', text)
    chars = [c for c in nfkd if '\u05D0' <= c <= '\u05EA' or c in ' \t']
    result = ''.join(chars)
    return result.replace('ך', 'כ').replace('ם', 'מ').replace('ן', 'נ').replace('ף', 'פ').replace('ץ', 'צ')

def normalize_text(text):
    if not text: return ""
    nfkd = unicodedata.normalize('NFKD', text.lower())
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

_WORD_RE = re.compile(r'\S+')
_LATIN_WORD_RE = re.compile(r'\b\w+\b')
_VPL_RE = re.compile(r'([A-Z0-9]{2,5})\s+(\d+):(\d+)\s+(.+)', re.IGNORECASE)
_GREEK_ENDINGS = re.compile(r'(ους|οις|ων|ας|ης|ου|ος|ον|αι|εν|ες|ει|ις|ιν|αν|ην|ατ)$')

def get_hebrew_words(text): return [w for w in _WORD_RE.findall(normalize_hebrew(text)) if len(w) >= 2]
def get_greek_words(text): return [w for w in _WORD_RE.findall(normalize_greek(text)) if len(w) >= 2]
def get_trans_words(text): return _LATIN_WORD_RE.findall(normalize_text(text))

def detect_language(text):
    if not text: return "unknown"
    total = max(1, len(text.replace(" ", "")))
    heb_count = sum(1 for c in text if '\u05D0' <= c <= '\u05EA')
    grk_count = sum(1 for c in text if '\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF')
    if (heb_count / total) > 0.3: return "hebrew"
    if (grk_count / total) > 0.3: return "greek"
    return "latin"

_FINAL_TO_MEDIAL = str.maketrans('ךםןףץ', 'כמנפצ')
_HEBREW_ROOT_MAP = {k.translate(_FINAL_TO_MEDIAL): k for k in POLYSEMY if any('\u05D0' <= c <= '\u05EA' for c in k)}
_HEBREW_ROOTS = sorted(_HEBREW_ROOT_MAP.keys(), key=len, reverse=True)
_GREEK_ROOTS = sorted([k for k in POLYSEMY if any('\u0370' <= c <= '\u03FF' for c in k)], key=len, reverse=True)

def stem_greek(word):
    candidates = [word]
    stripped = _GREEK_ENDINGS.sub('', word)
    if stripped and stripped != word and len(stripped) >= 3: candidates.append(stripped)
    return candidates

_HEB_PREFIXES = frozenset("והבכלמש")
def strip_hebrew_prefixes_multi(word):
    stripped = word
    for _ in range(2):
        if len(stripped) > 3 and stripped[0] in _HEB_PREFIXES: stripped = stripped[1:]
        else: break
    return stripped

def matches_polysemy(word, lang):
    if lang == "hebrew":
        for cand in [word, strip_hebrew_prefixes_multi(word)]:
            for root in _HEBREW_ROOTS:
                if (len(root) < 3 and cand == root) or (len(root) >= 3 and cand.startswith(root)):
                    return _HEBREW_ROOT_MAP[root]
    else:
        for cand in stem_greek(word):
            for root in _GREEK_ROOTS:
                if (len(root) < 4 and cand == root) or (len(root) >= 4 and cand.startswith(root)):
                    return root
    return None

# ── ENHANCED GENEALOGY DETECTION (OpenAI Integration) ──
def is_name_list(words, en_text=""):
    if not words or len(words) < 4: return False
    short_ratio = sum(1 for w in words if len(w) <= 3) / len(words)
    if en_text and re.search(r'\b(begat|son of|sons of|daughter|descendants)\b', en_text, re.I) and short_ratio > 0.5: 
        return True
    return len(words) > 8 and short_ratio > 0.7

_STOP_WORDS = frozenset({"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "is", "was", "are", "were", "be", "been", "am", "it", "he", "she", "they", "them", "his", "her", "its", "their", "this", "that", "not", "no", "i", "we", "you", "my", "your", "our", "shall", "will", "had", "has", "have", "do", "did", "does", "so", "if", "who", "whom", "which", "what", "when", "where", "there", "then", "also", "as", "up", "out", "into", "upon", "all", "me", "us", "him", "och", "i", "att", "det", "som", "en", "ett", "den", "av", "till", "med", "han", "var", "jag", "de", "på", "är", "vi", "har", "du", "inte", "för", "om", "sin", "dem", "hade", "sig", "hans", "från", "hon", "ska", "kan", "mot", "så", "alla", "ut", "men", "där"})

def token_jaccard(a, b):
    sa = set(get_trans_words(a)) - _STOP_WORDS
    sb = set(get_trans_words(b)) - _STOP_WORDS
    return len(sa & sb) / len(sa | sb) if (sa | sb) else 0.0

def shannon_entropy(words):
    if not words: return 0.0
    freq = defaultdict(int)
    for w in words: freq[w] += 1
    total = len(words)
    return -sum((c/total)*math.log2(c/total) for c in freq.values())

# ===================== ANALYZER =====================
class BibleAnalyzer:
    def __init__(self, excluded_books=None):
        self.verses = defaultdict(dict)
        self.excluded_books = excluded_books or set()
        if SBERT_AVAILABLE:
            print("🧠 Loading Semantic Model (all-MiniLM-L6-v2)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def load_all(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        for code, info in VERSIONS.items():
            zip_path = os.path.join(DATA_DIR, info["url"].split("/")[-1]) if "url" in info else None
            subdir = os.path.join(DATA_DIR, info["subdir"])
            if zip_path and not os.path.exists(zip_path):
                print(f"Downloading {info['name']}...")
                try:
                    r = requests.get(info["url"], stream=True, timeout=60)
                    with open(zip_path, "wb") as f:
                        for chunk in r.iter_content(8192): f.write(chunk)
                except Exception as e:
                    print(f"   ⚠ Download failed: {e}")
                    continue
            if zip_path and not os.path.exists(subdir):
                try:
                    with zipfile.ZipFile(zip_path) as z: z.extractall(DATA_DIR)
                except Exception as e:
                    print(f"   ⚠ Unzip failed: {e}")
                    continue
            vpl_path = os.path.join(subdir, info["file"])
            if not os.path.exists(vpl_path): continue
            print(f"Loading {info['name']}...")
            data = self.parse_vpl(vpl_path)
            for key, text in data.items():
                if key[0].upper() not in self.excluded_books:
                    self.verses[key][code] = text

    def parse_vpl(self, file_path):
        verses = {}
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = _VPL_RE.match(line.strip())
                if m:
                    book, ch, v, text = m.groups()
                    if len(text.strip()) > 3: verses[(book.upper(), int(ch), int(v))] = text.strip()
        return verses

    def compute_scores(self, row, semantic_div):
        gr, heb, lxx = [str(row.get(k, "")) for k in ["gr", "heb", "lxx"]]
        orig = gr or heb or lxx
        en_text = str(row.get("en", ""))
        lang = detect_language(orig)
        words = get_hebrew_words(orig) if lang == "hebrew" else get_greek_words(orig) if lang == "greek" else get_trans_words(orig)
        
        en_len = max(1, len(en_text.split()))
        orig_len = max(1, len(orig.split()))
        length_ratio = round(abs(orig_len - en_len) / en_len * 100, 1)

        matched_roots = [matches_polysemy(w, lang) for w in words]
        matched_roots = [r for r in matched_roots if r and len(POLYSEMY.get(r, [])) > 1]
        unique_roots = list(set(matched_roots))
        
        if is_name_list(words, en_text):
            lex_ambiguity = 0.0
            name_list_flag = True
        else:
            lex_ambiguity = min(sum(len(POLYSEMY.get(r, [])) * 4 for r in matched_roots), 100)
            name_list_flag = False

        # Morphological Complexity
        ttr = (len(set(words)) / max(1, len(words))) * 100
        entropy = shannon_entropy(words) * 15
        morph_complexity = round(min((ttr * 0.5 + entropy * 0.5), 100), 1)

        # Theological Boost
        theo_keywords = []
        weights = THEOLOGICAL_WEIGHTS_HEBREW if lang == "hebrew" else THEOLOGICAL_WEIGHTS_GREEK
        weight_sum = sum(weights.get(r, 0) for r in unique_roots)
        keyword_density = len([r for r in unique_roots if weights.get(r, 0) > 0]) / max(1, len(words))
        theo_boost = min(weight_sum * (1.0 + keyword_density * 5), 30.0)
        theo_normalized = min(theo_boost * (100 / 30), 100)

        # ── STRICTER STATISTICAL GUARDS (Grok Integration) ──
        trans_div = semantic_div
        if en_len < 7: 
            trans_div = 0.0
        elif en_len < 12: 
            trans_div = min(trans_div, 40.0)

        # Hebrew-LXX baseline flag (Gemini core)
        heb_lxx_flag = 5.0 if heb and lxx else 0.0

        is_ot = bool(heb)
        if is_ot:
            composite = round(0.15*length_ratio + 0.30*trans_div + 0.25*lex_ambiguity + 0.15*morph_complexity + 0.10*theo_normalized + 0.05*heb_lxx_flag, 1)
        else:
            composite = round(0.15*length_ratio + 0.35*trans_div + 0.25*lex_ambiguity + 0.10*morph_complexity + 0.15*theo_normalized, 1)

        interp_difficulty = round(0.40*lex_ambiguity + 0.35*trans_div + 0.25*morph_complexity, 1)

        reasons = []
        if name_list_flag: reasons.append("⚠ name-list suppressed")
        if len(unique_roots) > 0 and not name_list_flag: 
            senses = [f"{r}({'/'.join(POLYSEMY[r][:2])})" for r in unique_roots[:3]]
            reasons.append(f"{len(matched_roots)} polysemous: {'; '.join(senses)}")
        if trans_div > 25: reasons.append(f"Semantic divergence {trans_div}%")
        if theo_boost > 10: reasons.append(f"Theological density (+{theo_boost:.1f})")
        if heb_lxx_flag > 0: reasons.append("MT/LXX source variant baseline")

        return pd.Series({
            "length_ratio": length_ratio, "lex_ambiguity": lex_ambiguity,
            "morph_complexity": morph_complexity, "trans_divergence": trans_div,
            "theo_boost": theo_boost, "interp_difficulty": interp_difficulty,
            "composite": composite, "reasons": reasons, "name_list": name_list_flag
        })

    def analyze(self, mode, excluded_books, group=None):
        group_books = BOOK_GROUPS.get(group) if group else None
        rows = []
        for ref, texts in self.verses.items():
            book = ref[0]
            if book in excluded_books or "en" not in texts: continue
            if mode == "nt" and book not in NT_BOOKS: continue
            if mode == "ot" and book in NT_BOOKS: continue
            if group_books and book not in group_books: continue
            if any(k in texts for k in ("gr", "heb", "lxx")):
                rows.append({"ref": f"{book} {ref[1]}:{ref[2]}", "book": book, **texts})
        
        df = pd.DataFrame(rows).fillna("")
        if df.empty: return {}

        print(f"🧠 NLP Batch Processing {len(df)} verses...")
        trans_cols = [c for c in ["en", "web", "asv", "sv"] if c in df.columns]
        semantic_scores = []

        if SBERT_AVAILABLE and len(trans_cols) > 1:
            embeddings_dict = {}
            for col in trans_cols:
                print(f"   Vectorizing {col.upper()}...")
                embeddings_dict[col] = self.model.encode(df[col].tolist(), show_progress_bar=True, convert_to_tensor=True)
            
            print("   Calculating Cosine Similarity...")
            for idx in range(len(df)):
                valid_cols = [c for c in trans_cols if df.iloc[idx][c]]
                if len(valid_cols) < 2: semantic_scores.append(0.0); continue
                sims = []
                for i in range(len(valid_cols)):
                    for j in range(i+1, len(valid_cols)):
                        sims.append(util.cos_sim(embeddings_dict[valid_cols[i]][idx], embeddings_dict[valid_cols[j]][idx]).item())
                semantic_scores.append(round((1 - statistics.mean(sims)) * 100, 1))
        else:
            for idx in range(len(df)):
                t_list = [df.iloc[idx][c] for c in trans_cols if df.iloc[idx][c]]
                if len(t_list) < 2: semantic_scores.append(0.0); continue
                sims = [token_jaccard(t_list[i], t_list[j]) for i in range(len(t_list)) for j in range(i+1, len(t_list))]
                semantic_scores.append(round((1 - statistics.mean(sims)) * 100, 1))

        score_df = df.apply(lambda r: self.compute_scores(r, semantic_scores[r.name]), axis=1)
        df = pd.concat([df, score_df], axis=1)

        # SQLITE EXPORT (Gemini core)
        db_path = os.path.join(OUTPUT_DIR, f"nuance_v13_{mode}.db")
        df_sql = df.copy()
        df_sql['reasons'] = df_sql['reasons'].apply(lambda x: "; ".join(x))
        with sqlite3.connect(db_path) as conn: df_sql.to_sql("verses", conn, index=False, if_exists="replace")

        res = {}
        for label, col in {"overall_nuance_potential": "composite", "interpretation_difficulty": "interp_difficulty", "highest_lexical_ambiguity": "lex_ambiguity", "translation_divergence": "trans_divergence"}.items():
            res[label] = df.nlargest(TOP_N, col).to_dict(orient="records")
        
        res["_stats"] = {
            "total_verses": len(df), "avg_composite": round(df["composite"].mean(), 2),
            "avg_divergence": round(df["trans_divergence"].mean(), 2),
            "avg_interp_difficulty": round(df["interp_difficulty"].mean(), 2),
            "verses_with_polysemy": int((df["lex_ambiguity"] > 0).sum()),
            "verses_with_theo_boost": int((df["theo_boost"] > 0).sum()),
            "verses_name_list_suppressed": int(df["name_list"].sum())
        }
        return res

# ===================== RUN =====================
parser = argparse.ArgumentParser(description="Bible Nuance Analyzer v13.0")
parser.add_argument("--mode", choices=["nt", "ot", "both", "combined"], default="both")
parser.add_argument("--top", type=int, default=60)
parser.add_argument("--canon", choices=["all", "protestant", "catholic", "orthodox"], default="all")
parser.add_argument("--group", type=str, choices=list(BOOK_GROUPS.keys()))
args = parser.parse_args()
TOP_N = args.top

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
OUTPUT_DIR = f"results_{timestamp}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

analyzer = BibleAnalyzer(get_excluded_books(args.canon))
analyzer.load_all()

modes = ["nt", "ot"] if args.mode == "both" else [args.mode] if args.mode != "combined" else ["combined"]
for m in modes:
    print(f"\n🔍 Running {m.upper()} analysis...")
    res = analyzer.analyze(m, get_excluded_books(args.canon), args.group)
    if not res: continue
    
    with open(os.path.join(OUTPUT_DIR, f"{m}_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    # ── COMPREHENSIVE REPORTING (Claude Integration) ──
    with open(os.path.join(OUTPUT_DIR, f"summary_{m}.md"), "w", encoding="utf-8") as f:
        stats = res["_stats"]
        f.write(f"# Bible Nuance Report v13.0 – {m.upper()}\n\n")
        f.write(f"**Total verses**: {stats['total_verses']}\n")
        f.write(f"**Polysemy hits**: {stats['verses_with_polysemy']}\n")
        f.write(f"**Theological boost**: {stats['verses_with_theo_boost']}\n")
        f.write(f"**Name-lists suppressed**: {stats['verses_name_list_suppressed']}\n")
        f.write(f"**Avg composite**: {stats['avg_composite']}\n")
        f.write(f"**Avg divergence**: {stats['avg_divergence']}%\n")
        f.write(f"**Avg interpretation difficulty**: {stats['avg_interp_difficulty']}\n\n")

        f.write("## Top 10 Overall (Composite Nuance)\n")
        for r in res["overall_nuance_potential"][:10]:
            f.write(f"- **{r['ref']}** ({r['composite']}): {'; '.join(r['reasons'])}\n")

        f.write("\n## Top 10 Most Difficult to Interpret\n")
        for r in res["interpretation_difficulty"][:10]:
            f.write(f"- **{r['ref']}** – difficulty {r['interp_difficulty']:.1f}")
            if r.get("theo_boost", 0) > 0: f.write(f" ⭐")
            f.write(f"\n    • {'; '.join(r['reasons'])}\n")

        f.write("\n## Top 10 by Lexical Ambiguity\n")
        for r in res["highest_lexical_ambiguity"][:10]:
            f.write(f"- **{r['ref']}** – score {r['lex_ambiguity']:.1f}\n")

        f.write("\n## Top 10 by Translation Divergence\n")
        for r in res["translation_divergence"][:10]:
            f.write(f"- **{r['ref']}** – divergence {r['trans_divergence']:.1f}%\n")
            if r.get("en"):
                snippet = r['en'][:90]
                f.write(f"    KJV: {snippet}{'...' if len(r['en']) > 90 else ''}\n")

print(f"\n🎉 v13.0 COMPLETE! Folder: {OUTPUT_DIR}/")
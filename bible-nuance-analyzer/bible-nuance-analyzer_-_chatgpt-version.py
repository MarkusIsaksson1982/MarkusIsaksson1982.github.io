#!/usr/bin/env python3
"""
Bible Linguistic Ambiguity Analyzer v12.0

Major features
--------------
• Hebrew prefix + suffix normalization
• Greek morphological stemming
• Polysemy root detection
• Translation divergence scoring
• Hebrew vs LXX semantic divergence
• Morphological complexity scoring
• Explainable verse ranking

Input format expected:
VPL style:
BOOK CHAPTER:VERSE text

Example:
GEN 1:1 In the beginning God created the heaven and the earth
"""

import re
import math
import unicodedata
from collections import defaultdict, Counter

# ------------------------------------------------------------
# POLYSEMY ROOT DATABASE
# (abbreviated sample – extend in production)
# ------------------------------------------------------------

POLYSEMY = {
    # Hebrew
    "ידע": ["know", "experience", "sexual relations"],
    "רוח": ["spirit", "wind", "breath"],
    "נפש": ["soul", "life", "person"],
    "שלום": ["peace", "wholeness", "welfare"],
    "עלם": ["young woman", "hidden", "virgin?"],
    "משפט": ["judgment", "justice", "custom"],

    # Greek
    "λογ": ["word", "reason", "message", "account"],
    "πιστ": ["faith", "trust", "belief"],
    "χαρι": ["grace", "favor", "gift"],
    "πνευμ": ["spirit", "wind", "breath"],
    "δικαι": ["righteousness", "justice"],
}

# ------------------------------------------------------------
# STOP WORDS
# ------------------------------------------------------------

STOP_WORDS = {
    "the","and","of","to","in","a","that","is","for","on","with",
    "as","was","by","it","from","at","an","be"
}

# ------------------------------------------------------------
# SYNONYM NORMALIZATION
# ------------------------------------------------------------

SYNONYMS = {
    "charity": "love",
    "kingdom": "reign",
    "righteousness": "justice",
    "spirit": "spirit",
    "ghost": "spirit",
}

# ------------------------------------------------------------
# HEBREW NORMALIZATION
# ------------------------------------------------------------

HEB_PREFIXES = ("ו","ה","ב","כ","ל","מ","ש")
HEB_SUFFIXES = ("תי","נו","תם","תן","ים","ות","ה","ו")

def normalize_hebrew(word):

    # strip prefixes
    while len(word) > 3 and word[0] in HEB_PREFIXES:
        word = word[1:]

    # strip suffixes
    for s in HEB_SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 3:
            word = word[:-len(s)]
            break

    return word


# ------------------------------------------------------------
# GREEK NORMALIZATION
# ------------------------------------------------------------

GREEK_ENDINGS = (
    "ους","οις","ων","ας","ης","ου","ος","ον",
    "αι","εν","ες","ει","ις","ιν","αν","ην"
)

def normalize_greek(word):

    word = unicodedata.normalize("NFD", word)

    for ending in GREEK_ENDINGS:
        if word.endswith(ending) and len(word) > len(ending)+2:
            return word[:-len(ending)]

    return word


# ------------------------------------------------------------
# LANGUAGE DETECTION
# ------------------------------------------------------------

def detect_language(text):

    heb = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
    grk = sum(1 for c in text if '\u0370' <= c <= '\u03FF')

    total = len(text)

    if total == 0:
        return "unknown"

    if heb/total > 0.2:
        return "hebrew"

    if grk/total > 0.2:
        return "greek"

    return "other"


# ------------------------------------------------------------
# TOKENIZATION
# ------------------------------------------------------------

def tokenize(text):

    words = re.findall(r"[A-Za-z\u0370-\u03FF\u0590-\u05FF]+", text)

    words = [w.lower() for w in words]

    return words


# ------------------------------------------------------------
# SYNONYM COLLAPSE
# ------------------------------------------------------------

def normalize_synonyms(words):

    return [SYNONYMS.get(w, w) for w in words]


# ------------------------------------------------------------
# POLYSEMY SCORING
# ------------------------------------------------------------

def polysemy_score(words, lang):

    roots = set()

    for w in words:

        if lang == "hebrew":
            w = normalize_hebrew(w)

        elif lang == "greek":
            w = normalize_greek(w)

        for root in POLYSEMY:
            if w.startswith(root):
                roots.add(root)

    score = sum(len(POLYSEMY[r]) for r in roots)

    return score, roots


# ------------------------------------------------------------
# MORPHOLOGICAL COMPLEXITY
# ------------------------------------------------------------

def morphology_score(words):

    if not words:
        return 0

    total = len(words)

    unique = len(set(words))

    ttr = unique / total

    counts = Counter(words)

    entropy = -sum(
        (c/total) * math.log(c/total)
        for c in counts.values()
    )

    return (ttr + entropy) * 10


# ------------------------------------------------------------
# TRANSLATION DIVERGENCE
# ------------------------------------------------------------

def token_jaccard(a, b):

    A = set(a) - STOP_WORDS
    B = set(b) - STOP_WORDS

    if not A or not B:
        return 0

    return 1 - len(A & B) / len(A | B)


def translation_divergence(translations):

    scores = []

    langs = list(translations.keys())

    for i in range(len(langs)):
        for j in range(i+1, len(langs)):

            a = normalize_synonyms(tokenize(translations[langs[i]]))
            b = normalize_synonyms(tokenize(translations[langs[j]]))

            scores.append(token_jaccard(a,b))

    if not scores:
        return 0

    return sum(scores)/len(scores) * 100


# ------------------------------------------------------------
# HEBREW vs LXX DIVERGENCE
# ------------------------------------------------------------

def hebrew_lxx_divergence(hebrew, greek):

    hw = tokenize(hebrew)
    gw = tokenize(greek)

    hw = [normalize_hebrew(w) for w in hw]
    gw = [normalize_greek(w) for w in gw]

    hset = set(hw)
    gset = set(gw)

    if not hset or not gset:
        return 0

    return 1 - len(hset & gset) / len(hset | gset)


# ------------------------------------------------------------
# VERSE ANALYSIS
# ------------------------------------------------------------

def analyze_verse(ref, texts):

    explanation = {}

    # pick base text for morphology
    base_text = next(iter(texts.values()))

    words = tokenize(base_text)

    lang = detect_language(base_text)

    poly, roots = polysemy_score(words, lang)

    morph = morphology_score(words)

    trans_div = translation_divergence(texts)

    explanation["polysemy_roots"] = list(roots)
    explanation["polysemy_score"] = poly
    explanation["morphology"] = round(morph,2)
    explanation["translation_divergence"] = round(trans_div,2)

    score = poly*4 + morph + trans_div

    return score, explanation


# ------------------------------------------------------------
# ANALYZE BIBLE
# ------------------------------------------------------------

def analyze_bible(dataset):

    results = []

    for ref, texts in dataset.items():

        score, exp = analyze_verse(ref, texts)

        results.append((score, ref, exp))

    results.sort(reverse=True)

    return results


# ------------------------------------------------------------
# EXPLAINABLE OUTPUT
# ------------------------------------------------------------

def print_results(results, top=20):

    for score, ref, exp in results[:top]:

        print("="*60)
        print(ref)
        print("Score:", round(score,2))

        print("Polysemy roots:", exp["polysemy_roots"])
        print("Polysemy score:", exp["polysemy_score"])

        print("Morphology:", exp["morphology"])

        print("Translation divergence:", exp["translation_divergence"])


# ------------------------------------------------------------
# DEMO
# ------------------------------------------------------------

if __name__ == "__main__":

    # Example minimal dataset

    dataset = {

        "John 1:1": {
            "KJV": "In the beginning was the Word",
            "WEB": "In the beginning was the Word",
        },

        "Isaiah 7:14": {
            "KJV": "Behold a virgin shall conceive",
            "WEB": "Behold a young woman shall conceive",
        }
    }

    results = analyze_bible(dataset)

    print_results(results)

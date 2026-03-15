#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI Bible Nuance Analyzer
============================
An intentionally modular, stdlib-only implementation that blends
the strongest ideas from prior versions while keeping the scoring
transparent and easy to extend.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


# ===================== DATA CONFIG =====================
DATA_SOURCES = {
    "heb": {"subdir": "hbo_vpl", "file": "hbo_vpl.txt", "label": "Hebrew OT (WLC)"},
    "lxx": {"subdir": "grcbrent_vpl", "file": "grcbrent_vpl.txt", "label": "Greek LXX (Brenton)"},
    "gr": {"subdir": "grcmt_vpl", "file": "grcmt_vpl.txt", "label": "Greek NT (RP)"},
    "en": {"subdir": "eng-kjv_vpl", "file": "eng-kjv_vpl.txt", "label": "KJV"},
    "asv": {"subdir": "eng-asv_vpl", "file": "eng-asv_vpl.txt", "label": "ASV"},
    "web": {"subdir": "eng-web_vpl", "file": "eng-web_vpl.txt", "label": "WEB"},
    "sv": {"subdir": "swe1917_vpl", "file": "swe1917_vpl.txt", "label": "Swedish 1917"},
}

NT_BOOKS = {
    "MAT", "MRK", "LUK", "JHN", "ACT",
    "ROM", "1CO", "2CO", "GAL", "EPH", "PHP", "COL",
    "1TH", "2TH", "1TI", "2TI", "TIT", "PHM",
    "HEB", "JAS", "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
}

VPL_RE = re.compile(r"([A-Z0-9]{2,5})\s+(\d+):(\d+)\s+(.+)", re.IGNORECASE)


# ===================== POLYSEMY DICTIONARIES =====================
HEBREW_POLYSEMY = {
    "רוח": ["spirit", "wind", "breath", "mind"],
    "נפש": ["soul", "life", "person", "appetite", "desire"],
    "דבר": ["word", "thing", "matter", "affair", "plague"],
    "עולם": ["eternity", "world", "age", "long duration", "ancient"],
    "חסד": ["steadfast love", "mercy", "kindness", "loyalty"],
    "שלום": ["peace", "welfare", "wholeness", "prosperity"],
    "תורה": ["law", "instruction", "teaching", "direction"],
    "אמת": ["truth", "faithfulness", "reliability"],
    "צדק": ["righteousness", "justice", "rightness"],
    "צדקה": ["righteousness", "justice", "righteous act"],
    "משפט": ["judgment", "justice", "ordinance", "custom"],
    "כבוד": ["glory", "honor", "weight", "abundance"],
    "חטא": ["sin", "sin-offering", "purification offering"],
    "עון": ["iniquity", "guilt", "punishment"],
    "פשע": ["transgression", "rebellion", "crime"],
    "ברית": ["covenant", "alliance", "treaty", "agreement"],
    "גאל": ["redeem", "avenge", "kinsman-redeemer"],
    "כפר": ["atone", "cover", "ransom", "appease"],
    "קדש": ["holy", "consecrate", "set apart", "sacred"],
    "טמא": ["unclean", "defile", "impure"],
    "טהר": ["clean", "pure", "purify"],
    "ישע": ["save", "deliver", "rescue", "victory"],
    "שוב": ["return", "repent", "turn back", "restore"],
    "ידע": ["know", "perceive", "be acquainted", "experience"],
    "אהב": ["love", "like", "desire"],
    "ירא": ["fear", "revere", "be afraid", "awe"],
    "בטח": ["trust", "be confident", "rely on"],
    "חכמה": ["wisdom", "skill", "experience"],
    "בינה": ["understanding", "insight", "discernment"],
    "דעת": ["knowledge", "perception", "skill"],
    "לב": ["heart", "mind", "will", "inner person"],
    "כח": ["strength", "power", "might", "wealth"],
    "עז": ["strength", "might", "fierce", "strong"],
    "גבורה": ["might", "strength", "valor", "mighty deed"],
    "אלהים": ["God", "gods", "divine beings", "judges"],
    "יהוה": ["LORD", "Yahweh", "the Lord"],
    "אדון": ["lord", "master", "owner", "sovereign"],
    "מלך": ["king", "reign", "royal"],
    "משיח": ["anointed", "messiah", "Christ"],
    "עבד": ["servant", "slave", "worship", "serve", "work"],
    "בן": ["son", "child", "descendant", "member of group"],
    "עם": ["people", "nation", "kinfolk", "with"],
    "גוי": ["nation", "people", "Gentile", "heathen"],
    "ארץ": ["earth", "land", "country", "ground"],
    "שמים": ["heaven", "heavens", "sky"],
    "יום": ["day", "time", "period", "age"],
    "עלם": ["young woman", "virgin", "maiden"],
    "בתולה": ["virgin", "young woman", "maiden"],
    "חיל": ["strength", "army", "wealth", "valor"],
    "שם": ["name", "reputation", "fame", "there"],
    "פנים": ["face", "presence", "surface", "before"],
    "דרך": ["way", "road", "journey", "manner", "conduct"],
    "מות": ["death", "die", "dead"],
    "חיה": ["live", "life", "animal", "revive"],
    "שאול": ["Sheol", "grave", "pit", "underworld"],
    "הבל": ["breath", "vanity", "vapor", "meaningless"],
    "עצם": ["bone", "self", "substance", "strength"],
    "בשר": ["flesh", "body", "meat", "mankind"],
    "דם": ["blood", "bloodshed", "guilt"],
    "קרב": ["approach", "near", "offer", "inward parts"],
    "נשא": ["lift", "carry", "bear", "forgive", "take"],
    "שפט": ["judge", "govern", "vindicate", "punish"],
    "רע": ["evil", "bad", "friend", "calamity"],
    "טוב": ["good", "pleasant", "beautiful", "welfare"],
    "חן": ["grace", "favor", "charm"],
    "אמן": ["believe", "trust", "amen", "confirm"],
    "ברך": ["bless", "kneel", "praise", "curse (euphemism)"],
    "קרא": ["call", "read", "proclaim", "name"],
    "שמע": ["hear", "listen", "obey", "understand"],
    "ראה": ["see", "perceive", "experience", "provide"],
    "דרש": ["seek", "inquire", "require", "study"],
    "בקש": ["seek", "request", "desire"],
    "נביא": ["prophet", "spokesman", "seer"],
    "חזון": ["vision", "revelation", "oracle"],
    "משל": ["proverb", "parable", "allegory", "rule"],
    "אות": ["sign", "miracle", "omen", "mark"],
    "מופת": ["wonder", "portent", "sign", "miracle"],
    "כרת": ["cut", "cut off", "make covenant", "destroy"],
    "נחם": ["comfort", "relent", "repent", "be sorry"],
    "חרם": ["devoted thing", "ban", "destroy utterly"],
    "צור": ["rock", "fortress", "form", "besiege"],
}

GREEK_POLYSEMY = {
    "λογος": ["word", "reason", "account", "speech", "message", "matter"],
    "πνευμα": ["spirit", "wind", "breath", "Spirit"],
    "σαρξ": ["flesh", "body", "human nature", "sinful nature"],
    "ψυχη": ["soul", "life", "self", "person"],
    "αγαπη": ["love", "charity", "affection"],
    "χαρις": ["grace", "favor", "thanks", "gift"],
    "πιστις": ["faith", "belief", "trust", "faithfulness"],
    "δικαιοσυνη": ["righteousness", "justice", "justification"],
    "αμαρτια": ["sin", "sinfulness", "sin offering"],
    "νομος": ["law", "principle", "custom", "Torah"],
    "κοσμος": ["world", "universe", "adornment", "order"],
    "αιων": ["age", "eternity", "world", "era"],
    "βασιλεια": ["kingdom", "reign", "royal power", "sovereignty"],
    "δοξα": ["glory", "honor", "brightness", "splendor", "opinion"],
    "ειρηνη": ["peace", "harmony", "welfare", "wholeness"],
    "εκκλησια": ["church", "assembly", "congregation", "gathering"],
    "αληθεια": ["truth", "reality", "sincerity"],
    "ελπις": ["hope", "expectation", "trust"],
    "σοφια": ["wisdom", "skill", "insight"],
    "δυναμις": ["power", "miracle", "ability", "might"],
    "εξουσια": ["authority", "power", "right", "jurisdiction"],
    "κρισις": ["judgment", "condemnation", "decision", "justice"],
    "σωτηρια": ["salvation", "deliverance", "preservation"],
    "μετανοια": ["repentance", "change of mind", "conversion"],
    "παρακλητος": ["advocate", "helper", "comforter", "counselor"],
    "μυστηριον": ["mystery", "secret", "hidden truth"],
    "παραβολη": ["parable", "comparison", "illustration", "figure"],
    "σημειον": ["sign", "miracle", "wonder", "mark"],
    "μαρτυρια": ["testimony", "witness", "evidence"],
    "ευαγγελιον": ["gospel", "good news", "good tidings"],
    "αποστολος": ["apostle", "messenger", "envoy", "sent one"],
    "διακονια": ["ministry", "service", "mission", "relief"],
    "δουλος": ["servant", "slave", "bondservant"],
    "κυριος": ["lord", "master", "Lord", "sir", "owner"],
    "θεος": ["God", "god", "divine being"],
    "χριστος": ["Christ", "anointed", "Messiah"],
    "υιος": ["son", "descendant", "follower"],
    "πατηρ": ["father", "ancestor", "originator"],
    "αδελφος": ["brother", "fellow believer", "neighbor"],
    "λαος": ["people", "crowd", "nation"],
    "εθνος": ["nation", "Gentiles", "people"],
    "ιερον": ["temple", "sanctuary", "sacred place"],
    "θυσια": ["sacrifice", "offering", "victim"],
    "αιμα": ["blood", "bloodshed", "death"],
    "σταυρος": ["cross", "execution stake", "crucifixion"],
    "αναστασις": ["resurrection", "rising", "standing up"],
    "ζωη": ["life", "living", "eternal life"],
    "θανατος": ["death", "mortality", "deadly"],
    "κοινωνια": ["fellowship", "communion", "sharing"],
    "διαθηκη": ["covenant", "testament", "will"],
    "βαπτισμα": ["baptism", "immersion", "washing"],
    "παρουσια": ["coming", "presence", "arrival", "advent"],
    "αποκαλυψις": ["revelation", "unveiling", "disclosure"],
    "τελος": ["end", "goal", "purpose", "completion", "tax"],
    "αρχη": ["beginning", "ruler", "authority", "origin"],
    "πληρωμα": ["fullness", "completion", "fulfillment", "patch"],
    "οικονομια": ["stewardship", "administration", "plan"],
    "καταλλαγη": ["reconciliation", "restoration", "exchange"],
    "ιλασμος": ["propitiation", "atoning sacrifice", "expiation"],
    "απολυτρωσις": ["redemption", "release", "deliverance"],
    "δικαιωσις": ["justification", "acquittal", "vindication"],
    "αγιασμος": ["sanctification", "holiness", "consecration"],
}


# ===================== DATA STRUCTURES =====================
@dataclass(frozen=True)
class VerseKey:
    book: str
    chapter: int
    verse: int

    def ref(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}"


@dataclass
class VerseResult:
    reference: str
    score: float
    signals: Dict[str, float]
    polysemous_roots: List[str]
    explanations: List[str]
    texts: Dict[str, str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "reference": self.reference,
            "score": self.score,
            "signals": self.signals,
            "polysemous_roots": self.polysemous_roots,
            "explanations": self.explanations,
            "texts": self.texts,
        }


# ===================== BIBLE ANALYZER =====================
class BibleAnalyzer:
    """Loads, normalizes, and tokenizes VPL verse sources."""

    _LATIN_WORD_RE = re.compile(r"[a-z]+")

    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root
        self.verses: Dict[VerseKey, Dict[str, str]] = {}

    def load_sources(self) -> None:
        for code, info in DATA_SOURCES.items():
            vpl_path = self.data_root / info["subdir"] / info["file"]
            if not vpl_path.exists():
                continue
            for key, text in self.parse_vpl(vpl_path).items():
                if key not in self.verses:
                    self.verses[key] = {}
                self.verses[key][code] = text

    def parse_vpl(self, file_path: Path) -> Dict[VerseKey, str]:
        verses: Dict[VerseKey, str] = {}
        with file_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = VPL_RE.match(line)
                if not match:
                    continue
                book, chapter, verse, text = match.groups()
                text = text.strip()
                if not text:
                    continue
                key = VerseKey(book.upper(), int(chapter), int(verse))
                verses[key] = text
        return verses

    def normalize_hebrew(self, text: str) -> str:
        if not text:
            return ""
        nfkd = unicodedata.normalize("NFKD", text)
        chars = [
            c for c in nfkd
            if ("\u05d0" <= c <= "\u05ea") or c.isspace()
        ]
        normalized = "".join(chars)
        return normalized.translate(str.maketrans("ךםןףץ", "כמנפצ"))

    def normalize_greek(self, text: str) -> str:
        if not text:
            return ""
        nfkd = unicodedata.normalize("NFKD", text.lower())
        chars = [
            c for c in nfkd
            if ("\u0370" <= c <= "\u03ff")
            or ("\u1f00" <= c <= "\u1fff")
            or c.isspace()
        ]
        normalized = "".join(c for c in chars if not unicodedata.combining(c))
        return normalized.replace("ς", "σ")

    def normalize_latin(self, text: str) -> str:
        if not text:
            return ""
        nfkd = unicodedata.normalize("NFKD", text.lower())
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def tokenize(self, text: str, lang: str) -> List[str]:
        if not text:
            return []
        if lang == "hebrew":
            return [w for w in self.normalize_hebrew(text).split() if len(w) >= 2]
        if lang == "greek":
            return [w for w in self.normalize_greek(text).split() if len(w) >= 2]
        normalized = self.normalize_latin(text)
        return self._LATIN_WORD_RE.findall(normalized)

    def is_name_list(self, tokens: List[str], translation_text: str) -> bool:
        if len(tokens) < 6:
            return False
        short_ratio = sum(1 for t in tokens if len(t) <= 3) / len(tokens)
        if short_ratio > 0.65 and len(tokens) > 8:
            return True
        if translation_text:
            if re.search(r"\b(begat|son of|sons of|descendants)\b", translation_text, re.I):
                return True
        return False


# ===================== POLYSEMY ANALYZER =====================
class PolysemyAnalyzer:
    """Detects polysemous roots with Hebrew prefix stripping and Greek stemming."""

    _HEB_PREFIXES = frozenset("והבכלמש")
    _HEB_SUFFIXES = ("ים", "ות")
    _GREEK_ENDINGS = re.compile(
        r"(ους|οις|ων|ας|ης|ου|ος|ον|αι|εν|ες|ει|ις|ιν|αν|ην)$"
    )

    def __init__(self, hebrew_roots: Dict[str, List[str]], greek_roots: Dict[str, List[str]]) -> None:
        self.hebrew_roots = {self._normalize_hebrew_root(k): v for k, v in hebrew_roots.items()}
        self.greek_roots = {self._normalize_greek_root(k): v for k, v in greek_roots.items()}
        self._hebrew_keys = sorted(self.hebrew_roots.keys(), key=len, reverse=True)
        self._greek_keys = sorted(self.greek_roots.keys(), key=len, reverse=True)

    @staticmethod
    def _normalize_hebrew_root(root: str) -> str:
        nfkd = unicodedata.normalize("NFKD", root)
        chars = [c for c in nfkd if "\u05d0" <= c <= "\u05ea"]
        return "".join(chars).translate(str.maketrans("ךםןףץ", "כמנפצ"))

    @staticmethod
    def _normalize_greek_root(root: str) -> str:
        nfkd = unicodedata.normalize("NFKD", root.lower())
        chars = [
            c for c in nfkd
            if ("\u0370" <= c <= "\u03ff") or ("\u1f00" <= c <= "\u1fff")
        ]
        normalized = "".join(c for c in chars if not unicodedata.combining(c))
        return normalized.replace("ς", "σ")

    def _strip_hebrew_prefixes(self, word: str) -> str:
        stripped = word
        for _ in range(2):
            if len(stripped) > 3 and stripped[0] in self._HEB_PREFIXES:
                stripped = stripped[1:]
            else:
                break
        return stripped

    def _strip_hebrew_suffixes(self, word: str) -> str:
        for suffix in self._HEB_SUFFIXES:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        return word

    def _stem_greek(self, word: str) -> List[str]:
        candidates = [word]
        stripped = self._GREEK_ENDINGS.sub("", word)
        if stripped and len(stripped) >= 3:
            candidates.append(stripped)
        return candidates

    def detect_polysemy(self, tokens: List[str], lang: str) -> List[str]:
        matches: List[str] = []
        if lang == "hebrew":
            for token in tokens:
                pref = self._strip_hebrew_prefixes(token)
                suff = self._strip_hebrew_suffixes(token)
                pref_suff = self._strip_hebrew_suffixes(pref)
                candidates = {token, pref, suff, pref_suff}
                for candidate in candidates:
                    for root in self._hebrew_keys:
                        if (len(root) <= 3 and candidate == root) or (
                            len(root) > 3 and candidate.startswith(root)
                        ):
                            matches.append(root)
                            break
        elif lang == "greek":
            for token in tokens:
                for candidate in self._stem_greek(token):
                    for root in self._greek_keys:
                        if (len(root) <= 3 and candidate == root) or (
                            len(root) > 3 and candidate.startswith(root)
                        ):
                            matches.append(root)
                            break
        return matches

    def polysemy_score(self, tokens: List[str], lang: str) -> Tuple[float, List[str]]:
        matches = self.detect_polysemy(tokens, lang)
        unique = sorted(set(matches))
        score = 0.0
        if lang == "hebrew":
            score = sum(len(self.hebrew_roots.get(root, [])) * 4 for root in matches)
        elif lang == "greek":
            score = sum(len(self.greek_roots.get(root, [])) * 4 for root in matches)
        return min(score, 100.0), unique


# ===================== TRANSLATION ANALYZER =====================
class TranslationAnalyzer:
    """Computes translation divergence via token Jaccard similarity."""

    _STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
        "with", "by", "from", "is", "was", "are", "were", "be", "been", "am",
        "it", "he", "she", "they", "them", "his", "her", "its", "their", "this",
        "that", "not", "no", "i", "we", "you", "my", "your", "our", "shall",
        "will", "had", "has", "have", "do", "did", "does", "so", "if", "who",
        "whom", "which", "what", "when", "where", "there", "then", "also", "as",
        "unto", "thee", "thy", "thou", "ye", "unto", "unto", "hath",
    }

    def token_jaccard(self, a_tokens: Iterable[str], b_tokens: Iterable[str]) -> float:
        a_set = {t for t in a_tokens if t not in self._STOPWORDS}
        b_set = {t for t in b_tokens if t not in self._STOPWORDS}
        if not a_set or not b_set:
            return 0.0
        return len(a_set & b_set) / len(a_set | b_set)

    def translation_divergence(
        self,
        translation_tokens: Dict[str, List[str]],
        base_len: int,
    ) -> Tuple[float, Optional[str]]:
        tokens = [t for t in translation_tokens.values() if t]
        if len(tokens) < 2:
            return 0.0, None
        sims: List[float] = []
        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens)):
                sims.append(self.token_jaccard(tokens[i], tokens[j]))
        divergence = round((1 - statistics.mean(sims)) * 100, 1) if sims else 0.0

        if base_len < 7:
            return 0.0, "short verse: translation divergence suppressed"
        if base_len < 12 and divergence > 40:
            return 40.0, "short verse: translation divergence capped"
        return divergence, None


# ===================== MORPHOLOGY ANALYZER =====================
class MorphologyAnalyzer:
    """Computes lexical density metrics: TTR and Shannon entropy."""

    def entropy(self, tokens: List[str]) -> float:
        if not tokens:
            return 0.0
        freq: Dict[str, int] = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        total = len(tokens)
        return -sum((c / total) * math.log2(c / total) for c in freq.values())

    def type_token_ratio(self, tokens: List[str]) -> float:
        if not tokens:
            return 0.0
        return len(set(tokens)) / len(tokens)

    def morphological_complexity(self, tokens: List[str]) -> Tuple[float, float, float]:
        if not tokens:
            return 0.0, 0.0, 0.0
        ttr = self.type_token_ratio(tokens) * 100
        entropy = self.entropy(tokens) * 15
        score = min(100.0, (ttr + entropy) / 2)
        return round(score, 1), round(ttr, 1), round(entropy, 2)


# ===================== TRADITION ANALYZER =====================
class TraditionAnalyzer:
    """Compares Hebrew and LXX wording via structural and lexical divergence."""

    def hebrew_lxx_divergence(self, hebrew_tokens: List[str], lxx_tokens: List[str]) -> float:
        if not hebrew_tokens or not lxx_tokens:
            return 0.0
        len_div = abs(len(hebrew_tokens) - len(lxx_tokens)) / max(len(hebrew_tokens), len(lxx_tokens))
        heb_ttr = len(set(hebrew_tokens)) / len(hebrew_tokens)
        lxx_ttr = len(set(lxx_tokens)) / len(lxx_tokens)
        ttr_div = abs(heb_ttr - lxx_ttr)
        score = (0.6 * len_div + 0.4 * ttr_div) * 100
        return round(min(score + 5.0, 100.0), 1)


# ===================== SCORING ENGINE =====================
class ScoringEngine:
    """Combines signals into a composite ambiguity score."""

    def compute_composite_score(self, signals: Dict[str, float], is_ot: bool) -> float:
        if is_ot:
            weights = {
                "polysemy_score": 0.30,
                "translation_divergence": 0.20,
                "morphological_complexity": 0.20,
                "hebrew_lxx_divergence": 0.30,
            }
        else:
            weights = {
                "polysemy_score": 0.35,
                "translation_divergence": 0.30,
                "morphological_complexity": 0.35,
                "hebrew_lxx_divergence": 0.0,
            }
        score = sum(signals.get(k, 0.0) * w for k, w in weights.items())
        return round(score, 1)


# ===================== REPORTING =====================
class ReportGenerator:
    """Ranks verses and exports results."""

    def rank_verses(self, results: List[VerseResult], top_n: int) -> List[VerseResult]:
        return sorted(results, key=lambda r: r.score, reverse=True)[:top_n]

    def generate_explanations(self, result: VerseResult) -> List[str]:
        return result.explanations

    def export_results(self, ranked: List[VerseResult], output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / "top_ambiguity_verses.json"
        md_path = output_dir / "top_ambiguity_verses.md"

        payload = {
            "count": len(ranked),
            "top_verses": [r.to_dict() for r in ranked],
        }
        with json_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

        with md_path.open("w", encoding="utf-8") as handle:
            handle.write("# Top Ambiguity Verses\n\n")
            for idx, result in enumerate(ranked, 1):
                handle.write(f"{idx}. {result.reference} — Score {result.score}\n")
                if result.explanations:
                    handle.write(f"Signals: {' | '.join(result.explanations)}\n")
                handle.write("\n")


# ===================== MAIN =====================
def find_data_root(explicit: Optional[str] = None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        return path

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    candidates = [
        script_dir / "data"
	
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "No data directory found. Provide --data-root pointing at a VPL data folder."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenAI Bible Nuance Analyzer")
    parser.add_argument("--data-root", type=str, default=None, help="Path to VPL data folder")
    parser.add_argument("--top", type=int, default=60, help="Number of verses to rank")
    parser.add_argument("--mode", choices=["ot", "nt", "both"], default="both")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_root = find_data_root(args.data_root)
    analyzer = BibleAnalyzer(data_root)
    analyzer.load_sources()

    polysemy = PolysemyAnalyzer(HEBREW_POLYSEMY, GREEK_POLYSEMY)
    translation = TranslationAnalyzer()
    morphology = MorphologyAnalyzer()
    tradition = TraditionAnalyzer()
    scorer = ScoringEngine()
    reporter = ReportGenerator()

    results: List[VerseResult] = []

    for key, texts in analyzer.verses.items():
        if args.mode == "ot" and key.book in NT_BOOKS:
            continue
        if args.mode == "nt" and key.book not in NT_BOOKS:
            continue

        orig_lang = "latin"
        orig_text = ""
        if "heb" in texts:
            orig_lang = "hebrew"
            orig_text = texts["heb"]
        elif "gr" in texts:
            orig_lang = "greek"
            orig_text = texts["gr"]
        elif "lxx" in texts:
            orig_lang = "greek"
            orig_text = texts["lxx"]

        if not orig_text:
            continue

        orig_tokens = analyzer.tokenize(orig_text, orig_lang)
        if not orig_tokens:
            continue

        poly_score, poly_roots = polysemy.polysemy_score(orig_tokens, orig_lang)
        name_list = analyzer.is_name_list(orig_tokens, texts.get("en", ""))
        if name_list:
            poly_score = 0.0

        trans_texts = {k: texts[k] for k in ("en", "asv", "web") if k in texts}
        trans_tokens = {
            k: analyzer.tokenize(v, "latin") for k, v in trans_texts.items()
        }
        base_len = len(analyzer.tokenize(texts.get("en", ""), "latin")) if "en" in texts else 0
        trans_div, trans_note = translation.translation_divergence(trans_tokens, base_len)

        morph_score, ttr, entropy = morphology.morphological_complexity(orig_tokens)

        heb_tokens = analyzer.tokenize(texts.get("heb", ""), "hebrew") if "heb" in texts else []
        lxx_tokens = analyzer.tokenize(texts.get("lxx", ""), "greek") if "lxx" in texts else []
        heb_lxx_div = tradition.hebrew_lxx_divergence(heb_tokens, lxx_tokens)

        signals = {
            "polysemy_score": poly_score,
            "translation_divergence": trans_div,
            "morphological_complexity": morph_score,
            "hebrew_lxx_divergence": heb_lxx_div,
        }
        score = scorer.compute_composite_score(signals, is_ot=("heb" in texts))

        explanations: List[str] = []
        if name_list:
            explanations.append("name-list detected (polysemy suppressed)")
        if poly_roots and not name_list:
            explanations.append(f"polysemous roots: {', '.join(poly_roots[:3])}")
        if heb_lxx_div > 0:
            explanations.append(f"Hebrew/LXX divergence {heb_lxx_div:.1f}")
        if trans_div > 0:
            explanations.append(f"translation divergence {trans_div:.1f}")
        if trans_note:
            explanations.append(trans_note)
        if morph_score > 0:
            explanations.append(f"morphological complexity {morph_score:.1f} (TTR {ttr:.1f}, H {entropy:.2f})")

        results.append(
            VerseResult(
                reference=key.ref(),
                score=score,
                signals=signals,
                polysemous_roots=poly_roots,
                explanations=explanations,
                texts={k: v for k, v in texts.items()},
            )
        )

    ranked = reporter.rank_verses(results, args.top)
    output_dir = Path(__file__).resolve().parent / "results"
    reporter.export_results(ranked, output_dir)

    print(f"Analyzed {len(results)} verses. Wrote {len(ranked)} results to {output_dir}")


if __name__ == "__main__":
    main()

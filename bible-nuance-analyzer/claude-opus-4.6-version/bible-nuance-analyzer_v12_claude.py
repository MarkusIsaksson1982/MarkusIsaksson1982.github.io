#!/usr/bin/env python3
"""
Bible Nuance Analyzer v12.0 — Claude Edition
=============================================
Changes from v11.0 (integrating best ideas from OpenAI, Gemini, Grok versions):

  1. HEBREW SUFFIX STRIPPING — strips plural markers ים,ות and pronominal
     suffixes alongside prefix stripping, catching אלהים→אלה, תורות→תור etc.
     (from OpenAI's PolysemyAnalyzer)
  2. GREEK SIGMA NORMALIZATION — maps final sigma ς→σ before matching,
     fixing missed matches on word-final forms (from OpenAI)
  3. STRICTER SHORT-VERSE TIERS — <7 words: divergence zeroed;
     7–11 words: capped at 40%; prevents false positives on short phrases
     (from Grok v12)
  4. SQLITE DATABASE EXPORT — generates queryable .db file for every run,
     enabling cross-referencing, SQL queries, and downstream tools
     (from Gemini v12)
  5. OPTIONAL SBERT SEMANTIC SIMILARITY — if sentence-transformers is
     installed, uses cosine similarity instead of token Jaccard for
     translation divergence; graceful fallback otherwise (from Gemini v12)
  6. HAPAX LEGOMENA DETECTION — flags words appearing only once in the
     entire corpus for each testament, as these are inherently harder to
     translate with confidence (new)
  7. LOG-RATIO LENGTH METRIC — replaces linear percentage with log-ratio,
     which is more stable across verse lengths (a 5→10 word difference is
     now scored the same as 50→100) (new)
  8. CROSS-LANGUAGE POLYSEMY ALIGNMENT — for Hebrew↔LXX pairs, checks
     whether polysemous roots in the Hebrew have corresponding polysemous
     Greek in the LXX, signaling where translators made interpretive
     choices (new)
  9. CSV EXPORT — alongside JSON and SQLite, generates a flat CSV of
     all scored verses for easy import into spreadsheets (new)
 10. All v11.0 features retained: prefix stripping, sense-weighted
     polysemy, density-based theological boost, interpretation difficulty,
     OT/NT composite weight split, name-list suppression, etc.
"""

import os
import zipfile
import requests
import re
import json
import math
import csv
import sqlite3
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd
from datetime import datetime
import argparse
import unicodedata
import statistics
from typing import Dict, List, Optional, Tuple, Set

# ── Optional NLP engine ──────────────────────────────────────────────────
try:
    from sentence_transformers import SentenceTransformer, util as sbert_util
    import torch
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False

# ===================== CONFIG =====================
DATA_DIR = "data"
TOP_N = 60

VERSIONS = {
    "gr":  {"name": "Greek_NT_RP",               "url": "https://ebible.org/Scriptures/grcmt_vpl.zip",     "subdir": "grcmt_vpl",     "file": "grcmt_vpl.txt",     "type": "nt"},
    "heb": {"name": "Hebrew_OT_WLC",             "url": "https://ebible.org/Scriptures/hbo_vpl.zip",      "subdir": "hbo_vpl",       "file": "hbo_vpl.txt",       "type": "ot"},
    "en":  {"name": "KJV",                       "url": "https://ebible.org/Scriptures/eng-kjv_vpl.zip",  "subdir": "eng-kjv_vpl",   "file": "eng-kjv_vpl.txt",   "type": "trans"},
    "web": {"name": "World English Bible",       "url": "https://ebible.org/Scriptures/eng-web_vpl.zip",  "subdir": "eng-web_vpl",   "file": "eng-web_vpl.txt",   "type": "trans"},
    "asv": {"name": "American Standard Version", "url": "https://ebible.org/Scriptures/eng-asv_vpl.zip",  "subdir": "eng-asv_vpl",   "file": "eng-asv_vpl.txt",   "type": "trans"},
    "sv":  {"name": "Swedish_1917",                                                                        "subdir": "swe1917_vpl",   "file": "swe1917_vpl.txt",   "type": "trans"},
    "lxx": {"name": "Brenton Septuagint",        "url": "https://ebible.org/Scriptures/grcbrent_vpl.zip", "subdir": "grcbrent_vpl",  "file": "grcbrent_vpl.txt",  "type": "ot"},
}

NT_BOOKS = {
    "MAT","MRK","LUK","JHN","ACT",
    "ROM","1CO","2CO","GAL","EPH","PHP","COL",
    "1TH","2TH","1TI","2TI","TIT","PHM",
    "HEB","JAS","1PE","2PE","1JN","2JN","3JN","JUD","REV",
}

# ── Canon definitions (bulletproof — from Grok's expanded list) ──────────
APOCRYPHA_PROTESTANT = {
    "BAR","SIR","JDT","1MA","2MA","WIS","TOB",
    "1ES","2ES","MAN","PS2","LJE","S3Y","SUS",
    "BEL","DAG","ODE","EZA","5EZ","6EZ",
    "3MA","4MA","PSS","ESG","ADT",
    "GES","LAO","JUB","ENO","4ES","TAZ","JSA","JSB",
    "SST","DNT","BLT",
    # Long-form eBible variants
    "BARU","SIRA","JUDI","TOBI","MACC1","MACC2","WISD",
    "1MACC","2MACC","3MACC","4MACC","1ESD","2ESD","MANA",
    "PS151","ADDES","BELDR","SUSAN","SONG3","PRAYAZ",
}
APOCRYPHA_CATHOLIC_EXTRA = {"3MA","4MA","PSS"}
APOCRYPHA_ORTHODOX_EXTRA: Set[str] = set()

def get_excluded_books(canon: str) -> Set[str]:
    """Always returns uppercase book codes for consistent matching."""
    if canon == "protestant":
        return {b.upper() for b in APOCRYPHA_PROTESTANT}
    elif canon == "catholic":
        return {b.upper() for b in APOCRYPHA_CATHOLIC_EXTRA}
    elif canon == "orthodox":
        return APOCRYPHA_ORTHODOX_EXTRA
    return set()

# ── Genre / book-group filters ───────────────────────────────────────────
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


# ===================== POLYSEMY DICTIONARY =====================
POLYSEMY = {
    # ══════════════════════════════════════════════════════════════
    #  HEBREW (~100 roots)
    # ══════════════════════════════════════════════════════════════
    "רוח":  ["spirit", "wind", "breath", "mind"],
    "נפש":  ["soul", "life", "person", "appetite", "desire"],
    "דבר":  ["word", "thing", "matter", "affair", "plague"],
    "עולם": ["eternity", "world", "age", "long duration", "ancient"],
    "חסד":  ["steadfast love", "mercy", "kindness", "loyalty", "lovingkindness"],
    "שלום": ["peace", "welfare", "completeness", "health", "prosperity"],
    "תורה": ["law", "instruction", "teaching", "direction"],
    "אמת":  ["truth", "faithfulness", "reliability", "stability"],
    "צדק":  ["righteousness", "justice", "rightness"],
    "צדקה": ["righteousness", "justice", "righteous act", "merit"],
    "משפט": ["judgment", "justice", "ordinance", "custom", "manner"],
    "כבוד": ["glory", "honor", "weight", "abundance"],
    "חטאת": ["sin", "sin-offering", "purification offering"],
    "עון":  ["iniquity", "guilt", "punishment"],
    "פשע":  ["transgression", "rebellion", "crime"],
    "ברית": ["covenant", "alliance", "treaty", "agreement"],
    "גאל":  ["redeem", "avenge", "kinsman-redeemer"],
    "כפר":  ["atone", "cover", "ransom", "appease"],
    "קדש":  ["holy", "consecrate", "set apart", "sacred"],
    "טמא":  ["unclean", "defile", "impure"],
    "טהר":  ["clean", "pure", "purify"],
    "ישע":  ["save", "deliver", "rescue", "victory"],
    "שוב":  ["return", "repent", "turn back", "restore"],
    "ידע":  ["know", "perceive", "be acquainted", "experience"],
    "אהב":  ["love", "like", "desire"],
    "ירא":  ["fear", "revere", "be afraid", "awe"],
    "בטח":  ["trust", "be confident", "rely on"],
    "חכמה": ["wisdom", "skill", "experience"],
    "בינה": ["understanding", "insight", "discernment"],
    "דעת":  ["knowledge", "perception", "skill"],
    "לב":   ["heart", "mind", "will", "inner person"],
    "כח":   ["strength", "power", "might", "wealth"],
    "עז":   ["strength", "might", "fierce", "strong"],
    "גבורה":["might", "strength", "valor", "mighty deed"],
    "אלהים":["God", "gods", "divine beings", "judges"],
    "יהוה": ["LORD", "Yahweh", "the Lord", "Jehovah"],
    "אדון": ["lord", "master", "owner", "sovereign"],
    "מלך":  ["king", "reign", "royal"],
    "משיח": ["anointed", "messiah", "Christ"],
    "עבד":  ["servant", "slave", "worship", "serve", "work"],
    "בן":   ["son", "child", "descendant", "member of group"],
    "עם":   ["people", "nation", "kinfolk", "with"],
    "גוי":  ["nation", "people", "Gentile", "heathen"],
    "ארץ":  ["earth", "land", "country", "ground"],
    "שמים": ["heaven", "heavens", "sky"],
    "יום":  ["day", "time", "period", "age"],
    "עלמה": ["young woman", "virgin", "maiden"],
    "בתולה":["virgin", "young woman", "maiden"],
    "חיל":  ["strength", "army", "wealth", "virtue", "valor"],
    "שם":   ["name", "reputation", "fame", "there"],
    "פנים": ["face", "presence", "surface", "before"],
    "דרך":  ["way", "road", "journey", "manner", "conduct"],
    "מות":  ["death", "die", "dead"],
    "חיה":  ["live", "life", "animal", "revive"],
    "שאול": ["Sheol", "grave", "pit", "underworld"],
    "הבל":  ["breath", "vanity", "vapor", "meaningless", "futile"],
    "עצם":  ["bone", "self", "substance", "strength"],
    "בשר":  ["flesh", "body", "meat", "mankind"],
    "דם":   ["blood", "bloodshed", "guilt"],
    "קרב":  ["approach", "near", "draw near", "offer", "inward parts"],
    "נשא":  ["lift", "carry", "bear", "forgive", "take"],
    "שפט":  ["judge", "govern", "vindicate", "punish"],
    "רע":   ["evil", "bad", "friend", "companion", "calamity"],
    "טוב":  ["good", "pleasant", "beautiful", "welfare"],
    "חן":   ["grace", "favor", "charm", "elegance"],
    "אמן":  ["believe", "trust", "faithful", "amen", "confirm"],
    "ברך":  ["bless", "kneel", "praise", "curse (euphemism)"],
    "קרא":  ["call", "read", "proclaim", "name", "encounter"],
    "שמע":  ["hear", "listen", "obey", "understand"],
    "ראה":  ["see", "perceive", "experience", "provide"],
    "דרש":  ["seek", "inquire", "require", "study"],
    "בקש":  ["seek", "request", "desire"],
    "נביא": ["prophet", "spokesman", "seer"],
    "חזון": ["vision", "revelation", "oracle"],
    "משל":  ["proverb", "parable", "allegory", "rule", "dominion"],
    "סלה":  ["selah", "pause", "lift up", "forever"],
    "אות":  ["sign", "miracle", "omen", "mark"],
    "מופת": ["wonder", "portent", "sign", "miracle"],
    "כרת":  ["cut", "cut off", "make (covenant)", "destroy"],
    "נחם":  ["comfort", "relent", "repent", "be sorry"],
    "חרם":  ["devoted thing", "ban", "destroy utterly", "net"],
    "צור":  ["rock", "fortress", "form", "besiege"],
    "מזמור":["psalm", "song", "melody"],
    "שיר":  ["song", "sing", "poem"],
    "תהלה": ["praise", "glory", "fame"],
    "מנחה": ["offering", "gift", "tribute", "grain offering"],
    "זבח":  ["sacrifice", "slaughter", "feast"],
    "עלה":  ["go up", "ascend", "burnt offering", "leaf"],
    "כהן":  ["priest", "minister", "serve"],
    "לוי":  ["Levi", "Levite", "joined"],
    "נזיר": ["Nazirite", "consecrated", "prince (of vine)"],
    "ערל":  ["uncircumcised", "forbidden", "blocked"],
    "גלה":  ["reveal", "uncover", "exile", "depart"],
    "סתר":  ["hide", "conceal", "secret", "shelter"],
    "פלא":  ["wonderful", "marvelous", "extraordinary", "miracle"],
    "תמים": ["blameless", "complete", "perfect", "whole"],
    "ישר":  ["upright", "straight", "right", "pleasing"],
    "עוה":  ["bend", "twist", "do wrong", "pervert"],
    "רשע":  ["wicked", "guilty", "criminal"],
    "נתן":  ["give", "set", "put", "allow", "yield"],
    "עשה":  ["do", "make", "accomplish", "offer"],
    "הלך":  ["walk", "go", "live", "behave"],
    "עמד":  ["stand", "serve", "endure", "establish"],
    "נצל":  ["deliver", "rescue", "strip", "plunder"],
    "פדה":  ["ransom", "redeem", "rescue"],
    "חלל":  ["profane", "pierce", "begin", "defile"],
    "כלה":  ["complete", "finish", "consume", "destroy"],
    "צבא":  ["host", "army", "warfare", "serve"],
    "נחל":  ["inherit", "possess", "brook", "valley"],
    "מלא":  ["fill", "be full", "fulfill", "consecrate"],
    "סור":  ["turn aside", "depart", "remove", "take away"],

    # ══════════════════════════════════════════════════════════════
    #  GREEK (~250 lemmas)
    # ══════════════════════════════════════════════════════════════
    # ── Core theological nouns ──
    "λογος":       ["word", "reason", "account", "speech", "message", "matter"],
    "πνευμα":      ["spirit", "wind", "breath", "Spirit"],
    "σαρξ":        ["flesh", "body", "human nature", "sinful nature"],
    "ψυχη":        ["soul", "life", "self", "person"],
    "αγαπη":       ["love", "charity", "affection"],
    "χαρις":       ["grace", "favor", "thanks", "gift"],
    "πιστις":      ["faith", "belief", "trust", "faithfulness", "conviction"],
    "δικαιοσυνη":  ["righteousness", "justice", "justification"],
    "αμαρτια":     ["sin", "sinfulness", "sin offering"],
    "νομος":       ["law", "principle", "custom", "Torah"],
    "κοσμος":      ["world", "universe", "adornment", "order"],
    "αιων":        ["age", "eternity", "world", "era"],
    "βασιλεια":    ["kingdom", "reign", "royal power", "sovereignty"],
    "δοξα":        ["glory", "honor", "brightness", "splendor", "opinion"],
    "ειρηνη":      ["peace", "harmony", "welfare", "wholeness"],
    "εκκλησια":    ["church", "assembly", "congregation", "gathering"],
    "αληθεια":     ["truth", "reality", "sincerity"],
    "ελπις":       ["hope", "expectation", "trust"],
    "σοφια":       ["wisdom", "skill", "insight"],
    "δυναμις":     ["power", "miracle", "ability", "might"],
    "εξουσια":     ["authority", "power", "right", "jurisdiction"],
    "κρισις":      ["judgment", "condemnation", "decision", "justice"],
    "σωτηρια":     ["salvation", "deliverance", "preservation"],
    "μετανοια":    ["repentance", "change of mind", "conversion"],
    "παρακλητος":  ["advocate", "helper", "comforter", "counselor"],
    "μυστηριον":   ["mystery", "secret", "hidden truth"],
    "παραβολη":    ["parable", "comparison", "illustration", "figure"],
    "σημειον":     ["sign", "miracle", "wonder", "mark"],
    "μαρτυρια":    ["testimony", "witness", "evidence"],
    "ευαγγελιον":  ["gospel", "good news", "good tidings"],
    "αποστολος":   ["apostle", "messenger", "envoy", "sent one"],
    "διακονια":    ["ministry", "service", "mission", "relief"],
    "δουλος":      ["servant", "slave", "bondservant"],
    "κυριος":      ["lord", "master", "Lord", "sir", "owner"],
    "θεος":        ["God", "god", "divine being"],
    "χριστος":     ["Christ", "anointed", "Messiah"],
    "υιος":        ["son", "descendant", "follower"],
    "πατηρ":       ["father", "ancestor", "originator"],
    "αδελφος":     ["brother", "fellow believer", "neighbor"],
    "λαος":        ["people", "crowd", "nation"],
    "εθνος":       ["nation", "Gentiles", "people", "heathen"],
    "ιερον":       ["temple", "sanctuary", "sacred place"],
    "θυσια":       ["sacrifice", "offering", "victim"],
    "αιμα":        ["blood", "bloodshed", "death"],
    "σταυρος":     ["cross", "execution stake", "crucifixion"],
    "αναστασις":   ["resurrection", "rising", "standing up"],
    "ζωη":         ["life", "living", "eternal life"],
    "θανατος":     ["death", "mortality", "deadly"],
    "κοινωνια":    ["fellowship", "communion", "sharing", "participation"],
    "διαθηκη":     ["covenant", "testament", "will"],
    "βαπτισμα":    ["baptism", "immersion", "washing"],
    "παρουσια":    ["coming", "presence", "arrival", "advent"],
    "αποκαλυψις":  ["revelation", "unveiling", "disclosure", "appearing"],
    "τελος":       ["end", "goal", "purpose", "completion", "tax"],
    "αρχη":        ["beginning", "ruler", "authority", "origin", "corner"],
    "πληρωμα":     ["fullness", "completion", "fulfillment", "patch"],
    "οικονομια":   ["stewardship", "administration", "plan", "dispensation"],
    "καταλλαγη":   ["reconciliation", "restoration", "exchange"],
    "ιλασμος":     ["propitiation", "atoning sacrifice", "expiation"],
    "απολυτρωσις": ["redemption", "release", "deliverance"],
    "δικαιωσις":   ["justification", "acquittal", "vindication"],
    "αγιασμος":    ["sanctification", "holiness", "consecration"],
    "παραδοσις":   ["tradition", "handing over", "teaching"],
    "σκανδαλον":   ["stumbling block", "offense", "trap", "snare"],
    "τυπος":       ["type", "pattern", "example", "model", "mark"],
    "εικων":       ["image", "likeness", "form", "representation"],
    "μορφη":       ["form", "nature", "appearance"],
    "πληροω":      ["fulfill", "fill", "complete", "accomplish"],
    "καιρος":      ["time", "season", "opportune moment", "age"],
    "ημερα":       ["day", "time", "period", "judgment day"],
    "σκοτος":      ["darkness", "evil", "ignorance"],
    "φως":         ["light", "illumination", "revelation"],
    "αληθινος":    ["true", "genuine", "real"],
    "δικαιος":     ["righteous", "just", "upright", "innocent"],
    "πιστος":      ["faithful", "believing", "trustworthy", "reliable"],
    "παλαιος":     ["old", "ancient", "former", "obsolete"],
    "καινος":      ["new", "fresh", "novel", "renewed"],

    # ── High-frequency verbs ──
    "αγαπαω":      ["love", "cherish", "welcome"],
    "πιστευω":     ["believe", "trust", "have faith", "entrust"],
    "γινωσκω":     ["know", "understand", "perceive", "recognize"],
    "οιδα":        ["know", "understand", "recognize"],
    "θελω":        ["wish", "want", "will", "desire"],
    "δει":         ["must", "it is necessary", "ought"],
    "λεγω":        ["say", "tell", "speak", "mean", "call"],
    "λαλεω":       ["speak", "talk", "utter", "preach"],
    "ακουω":       ["hear", "listen", "obey", "understand"],
    "βλεπω":       ["see", "look", "beware", "perceive"],
    "οραω":        ["see", "perceive", "experience", "appear"],
    "ερχομαι":     ["come", "go", "appear", "arrive"],
    "πορευομαι":   ["go", "walk", "travel", "live", "conduct"],
    "περιπατεω":   ["walk", "live", "conduct oneself"],
    "εγειρω":      ["raise", "rise", "awaken", "restore"],
    "καλεω":       ["call", "invite", "name", "summon"],
    "αποστελλω":   ["send", "commission", "dispatch"],
    "διδωμι":      ["give", "grant", "allow", "yield", "produce"],
    "λαμβανω":     ["receive", "take", "accept", "obtain"],
    "εχω":         ["have", "hold", "possess", "be able"],
    "ποιεω":       ["do", "make", "produce", "perform", "cause"],
    "τιθημι":      ["put", "place", "set", "appoint", "lay down"],
    "ιστημι":      ["stand", "establish", "stop", "set"],
    "ζητεω":       ["seek", "look for", "desire", "demand"],
    "ευρισκω":     ["find", "discover", "obtain"],
    "κρινω":       ["judge", "decide", "condemn", "consider"],
    "σωζω":        ["save", "rescue", "heal", "preserve"],
    "απολλυμι":    ["destroy", "lose", "perish"],
    "αφιημι":      ["forgive", "leave", "allow", "abandon"],
    "δοξαζω":      ["glorify", "honor", "praise"],
    "αγιαζω":      ["sanctify", "make holy", "consecrate"],
    "βαπτιζω":     ["baptize", "immerse", "wash"],
    "κηρυσσω":     ["preach", "proclaim", "announce"],
    "διδασκω":     ["teach", "instruct"],
    "μαρτυρεω":    ["testify", "witness", "bear witness", "confirm"],
    "παρακαλεω":   ["encourage", "comfort", "exhort", "urge", "beseech"],
    "εντελλομαι":  ["command", "order", "instruct"],

    # ── Person/body/world nouns ──
    "σωμα":        ["body", "substance", "reality", "slave"],
    "μελος":       ["member", "part", "limb"],
    "προσωπον":    ["face", "presence", "surface", "appearance", "person"],
    "καρδια":      ["heart", "mind", "inner self", "will"],
    "συνειδησις":  ["conscience", "consciousness", "awareness"],
    "νους":        ["mind", "understanding", "thought", "purpose"],
    "φρονημα":     ["mindset", "way of thinking", "attitude"],
    "επιθυμια":    ["desire", "lust", "longing", "craving"],
    "οργη":        ["wrath", "anger", "indignation", "punishment"],
    "θλιψις":      ["tribulation", "affliction", "distress", "persecution"],
    "πειρασμος":   ["temptation", "trial", "test"],
    "παθημα":      ["suffering", "passion", "experience"],
    "χαρα":        ["joy", "gladness", "delight"],
    "ανθρωπος":    ["person", "human", "man", "humanity"],
    "γυνη":        ["woman", "wife"],
    "ανηρ":        ["man", "husband", "person"],
    "τεκνον":      ["child", "descendant", "follower"],
    "δεσποτης":    ["master", "lord", "owner", "sovereign"],
    "αρχων":       ["ruler", "prince", "authority", "official"],
    "πρεσβυτερος": ["elder", "older", "ancestor"],
    "διαβολος":    ["devil", "slanderer", "accuser"],
    "αγγελος":     ["angel", "messenger", "envoy"],
    "παραπτωμα":   ["trespass", "transgression", "sin", "false step"],
    "πλανη":       ["error", "deception", "delusion", "wandering"],
    "αποστασια":   ["apostasy", "rebellion", "abandonment"],
    "ανομια":      ["lawlessness", "wickedness", "iniquity"],
    "ασεβεια":     ["ungodliness", "impiety", "wickedness"],
    "υπομονη":     ["endurance", "patience", "perseverance", "steadfastness"],
    "ελεος":       ["mercy", "compassion", "pity"],
    "οικτιρμος":   ["compassion", "mercy", "pity"],
    "σπλαγχνα":    ["compassion", "affection", "tender mercies", "bowels"],
    "παρρησια":    ["boldness", "confidence", "openness", "freedom"],
    "υποταγη":     ["submission", "subjection", "obedience"],
    "ελευθερια":   ["freedom", "liberty"],
    "κληρονομια":  ["inheritance", "heritage", "possession"],
    "επαγγελια":   ["promise", "pledge", "announcement"],
    "προφητεια":   ["prophecy", "prediction", "prophetic gift"],
    "χαρισμα":     ["gift", "grace-gift", "spiritual gift", "favor"],
    "διδαχη":      ["teaching", "doctrine", "instruction"],
    "κερυγμα":     ["preaching", "proclamation", "message"],

    # ── Johannine, Petrine, apocalyptic, pastoral ──
    "αλαζονεια":   ["boasting", "arrogance", "pretension"],
    "μενω":        ["abide", "remain", "stay", "continue", "dwell"],
    "μαρτυς":      ["witness", "martyr"],
    "αρνιον":      ["lamb", "young sheep"],
    "θρονος":      ["throne", "seat of power"],
    "σφραγις":     ["seal", "mark", "signet"],
    "πληγη":       ["plague", "wound", "blow", "strike"],
    "δρακων":      ["dragon", "serpent"],
    "θηριον":      ["beast", "wild animal"],
    "πορνεια":     ["sexual immorality", "fornication", "idolatry"],
    "βδελυγμα":    ["abomination", "detestable thing"],
    "νικαω":       ["overcome", "conquer", "prevail"],
    "φιαλη":       ["bowl", "vial"],
    "κριμα":       ["judgment", "verdict", "condemnation", "lawsuit"],
    "φυσις":       ["nature", "natural order", "kind"],
    "ειδωλον":     ["idol", "image", "false god"],
    "γνωσις":      ["knowledge", "knowing", "recognition"],
    "επιγνωσις":   ["knowledge", "full knowledge", "recognition"],
    "φρονεω":      ["think", "set one's mind on", "be minded"],
    "λογιζομαι":   ["reckon", "count", "consider", "impute"],
    "νεκρος":      ["dead", "corpse", "lifeless"],
    "δοκιμη":      ["proof", "testing", "character", "experience"],
    "ευσεβεια":    ["godliness", "piety", "devotion"],
    "αρετη":       ["virtue", "excellence", "praise"],
    "πραυτης":     ["meekness", "gentleness", "humility"],
    "εγκρατεια":   ["self-control", "temperance"],
    "ταπεινοφροσυνη": ["humility", "modesty", "lowliness"],
    "αγαθος":      ["good", "beneficial", "useful", "generous"],
    "πονηρος":     ["evil", "bad", "wicked", "sick"],
    "αιωνιος":     ["eternal", "everlasting", "age-long"],
    "τελειος":     ["perfect", "complete", "mature"],
    "αγιος":       ["holy", "saint", "sacred", "set apart"],
    "πνευματικος": ["spiritual", "Spirit-filled", "supernatural"],
    "σαρκικος":    ["fleshly", "carnal", "worldly", "human"],
    "ψυχικος":     ["natural", "unspiritual", "soulish"],
    "καθαρος":     ["clean", "pure", "innocent"],
    "ελεεω":       ["have mercy", "show compassion", "pity"],
    "ιαομαι":      ["heal", "cure", "restore"],
    "θεραπευω":    ["heal", "serve", "treat", "care for"],
    "δαιμονιον":   ["demon", "evil spirit", "deity"],
    "πτωχος":      ["poor", "destitute", "beggarly"],
    "σκευος":      ["vessel", "instrument", "object", "body"],
    "στεφανος":    ["crown", "wreath", "prize"],
    "παιδεια":     ["discipline", "training", "education", "correction"],
    "λυτρον":      ["ransom", "redemption price"],
    "αντιλυτρον":  ["ransom", "corresponding price"],
    "μεσιτης":     ["mediator", "intermediary"],
    "αρχιερευς":   ["high priest", "chief priest"],
    "θυσιαστηριον": ["altar", "place of sacrifice"],
    "ιλαστηριον":  ["mercy seat", "propitiation", "place of atonement"],
    "περιτομη":    ["circumcision", "those circumcised"],
    "ακροβυστια":  ["uncircumcision", "Gentiles"],
    "δωρεαν":      ["freely", "without cause", "as a gift"],
    "ενεργεια":    ["working", "power", "activity", "energy"],
    "ευδοκια":     ["good pleasure", "will", "favor", "desire"],
    "ανακαινωσις": ["renewal", "renovation"],
    "μεταμορφοω":  ["transform", "transfigure", "change form"],
    "αποθνησκω":   ["die", "perish", "be put to death"],
    "ζαω":         ["live", "be alive", "come to life"],

    # ── Stem-prefix catch forms (for inflections) ──
    "πνευματ":     ["spirit", "wind", "breath"],
    "χαριτ":       ["grace", "favor", "gift"],
    "πιστε":       ["faith", "trust", "belief"],
    "αγαπ":        ["love", "charity"],
    "δικαιοσυν":   ["righteousness", "justice"],
    "αμαρτι":      ["sin", "sinfulness"],
    "σωτηρι":      ["salvation", "deliverance"],
    "βασιλει":     ["kingdom", "reign"],
    "εκκλησι":     ["church", "assembly"],
    "κοινωνι":     ["fellowship", "communion"],
    "μετανοι":     ["repentance", "turning"],
    "παρουσι":     ["coming", "presence"],
    "αποκαλυψ":    ["revelation", "unveiling"],
    "κατακρι":     ["condemnation", "judgment"],
    "επαγγελι":    ["promise", "pledge"],
    "κληρονομι":   ["inheritance", "heritage"],
    "προφητει":    ["prophecy", "prediction"],
    "χαρισματ":    ["gift", "grace-gift"],
    "ανομι":       ["lawlessness", "iniquity"],
    "ασεβει":      ["ungodliness", "impiety"],
    "ελευθερι":    ["freedom", "liberty"],
    "υπομον":      ["endurance", "patience"],
    "θλιψ":        ["tribulation", "distress"],
    "πειρασμ":     ["temptation", "trial"],
    "παθηματ":     ["suffering", "passion"],
    "νομ":         ["law", "principle", "custom"],
    "κοσμ":        ["world", "universe", "order"],
    "θρον":        ["throne", "seat of power"],
    "αρνι":        ["lamb", "young sheep"],
    "ελε":         ["mercy", "compassion"],
    "σαρκ":        ["flesh", "body", "human nature"],
    "ψυχ":         ["soul", "life", "self"],
    "δοξ":         ["glory", "honor", "splendor"],
    "λογ":         ["word", "reason", "account"],
    "εργ":         ["work", "deed", "action"],
    "οικ":         ["house", "household", "family"],
    "καρδι":       ["heart", "mind", "inner self"],
    "αιματ":       ["blood", "bloodshed"],
    "σωματ":       ["body", "substance"],
    "ονοματ":      ["name", "reputation"],
    "σπερματ":     ["seed", "offspring"],
    "κριματ":      ["judgment", "verdict"],
    "θανατ":       ["death", "mortality"],
    "σταυρ":       ["cross", "crucifixion"],
    "αναστα":      ["resurrection", "rising"],
    "μαρτυρ":      ["testimony", "witness"],
    "αποστολ":     ["apostle", "messenger"],
    "διακον":      ["ministry", "service"],
    "διαθηκ":      ["covenant", "testament"],
    "βαπτισ":      ["baptism", "immersion"],
    "μυστηρι":     ["mystery", "secret"],
    "παραβολ":     ["parable", "comparison"],
    "σημει":       ["sign", "miracle"],
    "ευαγγελι":    ["gospel", "good news"],
    "ιλασ":        ["propitiation", "atonement"],
    "απολυτρωσ":   ["redemption", "deliverance"],
    "σκανδαλ":     ["stumbling block", "offense"],
    "μεσιτ":       ["mediator", "intermediary"],
    "λυτρ":        ["ransom", "redemption"],
    "αρχιερ":      ["high priest", "chief priest"],
    "ανθρωπ":      ["person", "human", "man"],
    "γυναικ":      ["woman", "wife"],
    "ανδρ":        ["man", "husband"],
    "τεκν":        ["child", "descendant"],
    "πατρ":        ["father", "ancestor"],
    "αδελφ":       ["brother", "fellow believer"],
    "δουλ":        ["servant", "slave"],
    "κυρι":        ["lord", "master"],
    "θεο":         ["God", "god"],
    "χριστ":       ["Christ", "anointed"],
    "υιο":         ["son", "descendant"],
}


# ── WEIGHTED theological keywords ────────────────────────────────────────
THEOLOGICAL_WEIGHTS_HEBREW = {
    "רוח": 5, "נפש": 4, "חסד": 5, "צדק": 4, "צדקה": 4, "משפט": 3,
    "כבוד": 3, "חטאת": 5, "עון": 4, "פשע": 4, "ברית": 5, "כפר": 5,
    "קדש": 4, "משיח": 5, "גאל": 5, "ישע": 4, "תורה": 4, "שלום": 3,
    "אמת": 3, "הבל": 4, "עלמה": 5, "שאול": 4, "בתולה": 4,
    "אלהים": 3, "יהוה": 3, "דבר": 2,
}
THEOLOGICAL_WEIGHTS_GREEK = {
    "πνευμα": 5, "πιστις": 5, "δικαιοσυνη": 5, "χαρις": 5, "αγαπη": 4,
    "αμαρτια": 4, "σωτηρια": 4, "βασιλεια": 3, "εκκλησια": 3, "διαθηκη": 5,
    "παρουσια": 4, "αποκαλυψις": 4, "ιλασμος": 5, "απολυτρωσις": 5,
    "μετανοια": 4, "κοινωνια": 3, "μυστηριον": 3, "σαρξ": 4, "λογος": 4,
    "παρακλητος": 5, "σκανδαλον": 3, "σταυρος": 4, "αναστασις": 5,
    "βαπτισμα": 3, "χαρισμα": 3, "παραπτωμα": 3, "νομος": 3,
    "ιλαστηριον": 5, "μεσιτης": 4, "λυτρον": 5, "αρνιον": 4,
    # stem-prefix forms
    "πνευματ": 5, "πιστε": 5, "δικαιοσυν": 5, "χαριτ": 5, "αγαπ": 4,
    "αμαρτι": 4, "σωτηρι": 4, "βασιλει": 3, "αποκαλυψ": 4,
    "σαρκ": 4, "λογ": 4, "νομ": 3, "σταυρ": 4, "αναστα": 5,
    "διαθηκ": 5, "ιλασ": 5, "απολυτρωσ": 5, "λυτρ": 5, "μεσιτ": 4,
    "αρνι": 4, "μυστηρι": 3, "βαπτισ": 3, "σκανδαλ": 3,
}


# ===================== NORMALIZATION =====================
def normalize_greek(text: str) -> str:
    """Normalize Greek: lowercase, strip diacritics, normalize final sigma."""
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text.lower())
    result = ''.join(c for c in nfkd
                     if ('\u0370' <= c <= '\u03FF') or ('\u1F00' <= c <= '\u1FFF')
                     or c in ' \t')
    # v12: normalize final sigma ς→σ (from OpenAI) for consistent matching
    return result.replace('ς', 'σ')


def normalize_hebrew(text: str) -> str:
    """Normalize Hebrew: strip niqqud/cantillation, normalize final forms."""
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text)
    chars = [c for c in nfkd if '\u05D0' <= c <= '\u05EA' or c in ' \t']
    result = ''.join(chars)
    return result.replace('ך', 'כ').replace('ם', 'מ').replace('ן', 'נ').replace('ף', 'פ').replace('ץ', 'צ')


def normalize_text(text: str) -> str:
    """General normalization for Latin-script translations."""
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text.lower())
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


# ── Pre-compiled regex ───────────────────────────────────────────────────
_WORD_RE = re.compile(r'\S+')
_LATIN_WORD_RE = re.compile(r'\b\w+\b')
_VPL_RE = re.compile(r'([A-Z0-9]{2,5})\s+(\d+):(\d+)\s+(.+)', re.IGNORECASE)

# Greek ending-stripping regex (multi-char endings only)
_GREEK_ENDINGS = re.compile(
    r'(ους|οις|ων|ας|ης|ου|ος|ον|αι|εν|ες|ει|ις|ιν|αν|ην|ατ)$'
)


def get_hebrew_words(text: str) -> List[str]:
    return [w for w in _WORD_RE.findall(normalize_hebrew(text)) if len(w) >= 2]


def get_greek_words(text: str) -> List[str]:
    return [w for w in _WORD_RE.findall(normalize_greek(text)) if len(w) >= 2]


def get_trans_words(text: str) -> List[str]:
    return _LATIN_WORD_RE.findall(normalize_text(text))


def detect_language(text: str) -> str:
    """Ratio-based language detection."""
    if not text:
        return "unknown"
    total = max(1, len(text.replace(" ", "")))
    heb_count = sum(1 for c in text if '\u05D0' <= c <= '\u05EA')
    grk_count = sum(1 for c in text if '\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF')
    heb_ratio = heb_count / total
    grk_ratio = grk_count / total
    if heb_ratio > 0.3 and heb_ratio > grk_ratio:
        return "hebrew"
    if grk_ratio > 0.3 and grk_ratio > heb_ratio:
        return "greek"
    return "latin"


# ── Polysemy matching infrastructure ─────────────────────────────────────
_FINAL_TO_MEDIAL = str.maketrans('ךםןףץ', 'כמנפצ')

def _norm_heb_root(k: str) -> str:
    return k.translate(_FINAL_TO_MEDIAL)

_HEBREW_ROOT_MAP: Dict[str, str] = {}
for _k in POLYSEMY:
    if any('\u05D0' <= c <= '\u05EA' for c in _k):
        _HEBREW_ROOT_MAP[_norm_heb_root(_k)] = _k
_HEBREW_ROOTS = sorted(_HEBREW_ROOT_MAP.keys(), key=len, reverse=True)

# v12: Greek roots also get sigma-normalized for consistent matching
_GREEK_ROOTS = sorted(
    [k.replace('ς', 'σ') for k in POLYSEMY if any('\u0370' <= c <= '\u03FF' for c in k)],
    key=len, reverse=True
)
# Map normalized form back to original key
_GREEK_ROOT_MAP: Dict[str, str] = {}
for _k in POLYSEMY:
    if any('\u0370' <= c <= '\u03FF' for c in _k):
        _GREEK_ROOT_MAP[_k.replace('ς', 'σ')] = _k


def stem_greek(word: str) -> List[str]:
    """Crude Greek stemmer: strip common inflectional endings."""
    candidates = [word]
    stripped = _GREEK_ENDINGS.sub('', word)
    if stripped and stripped != word and len(stripped) >= 3:
        candidates.append(stripped)
    return candidates


# ── Hebrew prefix AND suffix stripping (v12: suffix from OpenAI) ─────────
_HEB_PREFIXES = frozenset("והבכלמש")
_HEB_SUFFIXES = ("ים", "ות", "יו", "הם", "הן", "ני", "כם")

def strip_hebrew_affixes(word: str) -> List[str]:
    """Generate candidate forms by stripping prefixes (up to 2) and suffixes."""
    candidates = [word]

    # Prefix stripping
    stripped = word
    for _ in range(2):
        if len(stripped) > 3 and stripped[0] in _HEB_PREFIXES:
            stripped = stripped[1:]
            candidates.append(stripped)
        else:
            break

    # Suffix stripping on each prefix-stripped candidate (from OpenAI)
    new_candidates = []
    for cand in candidates:
        for suffix in _HEB_SUFFIXES:
            if cand.endswith(suffix) and len(cand) > len(suffix) + 2:
                new_candidates.append(cand[:-len(suffix)])
    candidates.extend(new_candidates)

    return list(set(candidates))


def matches_polysemy(word: str, lang: str) -> Optional[str]:
    """Return matched root key or None."""
    if lang == "hebrew":
        min_prefix_len = 3
        candidates = strip_hebrew_affixes(word)
        for candidate in candidates:
            for root in _HEBREW_ROOTS:
                if len(root) < min_prefix_len:
                    if candidate == root:
                        return _HEBREW_ROOT_MAP[root]
                else:
                    if candidate.startswith(root):
                        return _HEBREW_ROOT_MAP[root]
        return None
    else:
        min_prefix_len = 4
        for root in _GREEK_ROOTS:
            if len(root) < min_prefix_len:
                if word == root:
                    return _GREEK_ROOT_MAP.get(root, root)
            else:
                if word.startswith(root):
                    return _GREEK_ROOT_MAP.get(root, root)
        # Try stemmed candidate
        for candidate in stem_greek(word):
            if candidate == word:
                continue
            for root in _GREEK_ROOTS:
                if len(root) < min_prefix_len:
                    if candidate == root:
                        return _GREEK_ROOT_MAP.get(root, root)
                else:
                    if candidate.startswith(root):
                        return _GREEK_ROOT_MAP.get(root, root)
        return None


# ── Name-list / genealogy detector ───────────────────────────────────────
_GENEALOGY_INDICATORS_EN = re.compile(
    r'\b(begat|begot|son of|daughter of|the sons of|children of|were born)\b',
    re.IGNORECASE
)

def is_name_list(words: List[str], en_text: str = "") -> bool:
    if not words or len(words) < 4:
        return False
    if en_text and _GENEALOGY_INDICATORS_EN.search(en_text):
        short = sum(1 for w in words if len(w) <= 3)
        if short / len(words) > 0.5:
            return True
    if len(words) > 8:
        short = sum(1 for w in words if len(w) <= 3)
        if short / len(words) > 0.7:
            return True
    return False


# ── Token Jaccard with stop-word filtering ────────────────────────────────
_STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "am", "it", "he", "she", "they", "them", "his", "her", "its", "their",
    "this", "that", "not", "no", "i", "we", "you", "my", "your", "our",
    "shall", "will", "had", "has", "have", "do", "did", "does", "so",
    "if", "who", "whom", "which", "what", "when", "where", "there", "then",
    "also", "as", "up", "out", "into", "upon", "all", "me", "us", "him",
    "unto", "thee", "thy", "thou", "ye", "hath",
    # Swedish
    "och", "att", "det", "som", "en", "ett", "den", "av", "till",
    "med", "han", "var", "jag", "de", "på", "är", "vi", "har", "du",
    "inte", "för", "om", "sin", "dem", "hade", "sig", "hans", "från",
    "hon", "ska", "kan", "mot", "så", "alla", "ut", "men", "där",
})


def token_jaccard(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    sa = set(get_trans_words(a)) - _STOP_WORDS
    sb = set(get_trans_words(b)) - _STOP_WORDS
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# ── Shannon entropy & TTR ────────────────────────────────────────────────
def shannon_entropy(words: List[str]) -> float:
    if not words:
        return 0.0
    freq = Counter(words)
    total = len(words)
    return -sum((c / total) * math.log2(c / total) for c in freq.values())


def type_token_ratio(words: List[str]) -> float:
    if not words:
        return 0.0
    return len(set(words)) / len(words)


# ===================== CLI =====================
parser = argparse.ArgumentParser(description="Bible Nuance Analyzer v12.0 (Claude)")
parser.add_argument("--mode", choices=["nt", "ot", "both", "combined"], default="both")
parser.add_argument("--top", type=int, default=60)
parser.add_argument("--canon", choices=["all", "protestant", "catholic", "orthodox"],
                    default="all")
parser.add_argument("--group", type=str, default=None,
                    choices=list(BOOK_GROUPS.keys()))
parser.add_argument("--sbert", action="store_true",
                    help="Use SBERT semantic similarity (requires sentence-transformers)")
parser.add_argument("--no-sqlite", action="store_true",
                    help="Skip SQLite export")
parser.add_argument("--no-csv", action="store_true",
                    help="Skip CSV export")
args = parser.parse_args()
TOP_N = args.top
EXCLUDED_BOOKS = get_excluded_books(args.canon)
USE_SBERT = args.sbert and SBERT_AVAILABLE

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
OUTPUT_DIR = f"results_{timestamp}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"🚀 Bible Nuance Analyzer v12.0 (Claude)")
print(f"Mode: {args.mode} | Canon: {args.canon} | Group: {args.group or 'all'} | Output: {OUTPUT_DIR}/")
if USE_SBERT:
    print(f"   NLP: SBERT semantic similarity enabled")
elif args.sbert and not SBERT_AVAILABLE:
    print(f"   ⚠ SBERT requested but sentence-transformers not installed; using Jaccard fallback")
else:
    print(f"   NLP: Token Jaccard (use --sbert for semantic similarity)")


# ===================== ANALYZER =====================
class BibleAnalyzer:
    def __init__(self, excluded_books: Optional[Set[str]] = None):
        self.verses: Dict[tuple, Dict[str, str]] = defaultdict(dict)
        self.excluded_books = excluded_books or set()
        self.corpus_word_freq: Dict[str, Counter] = {"nt": Counter(), "ot": Counter()}
        self.sbert_model = None
        if USE_SBERT:
            print("🧠 Loading SBERT model (all-MiniLM-L6-v2)...")
            self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

    def load_all(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        for code, info in VERSIONS.items():
            if "url" in info:
                zip_path = os.path.join(DATA_DIR, info["url"].split("/")[-1])
                if not os.path.exists(zip_path):
                    print(f"Downloading {info['name']}...")
                    try:
                        r = requests.get(info["url"], stream=True, timeout=60)
                        r.raise_for_status()
                        with open(zip_path, "wb") as f:
                            for chunk in r.iter_content(8192):
                                f.write(chunk)
                    except requests.RequestException as e:
                        print(f"   ⚠ Download failed for {info['name']}: {e}")
                        continue
                subdir = os.path.join(DATA_DIR, info["subdir"])
                if not os.path.exists(subdir):
                    try:
                        with zipfile.ZipFile(zip_path) as z:
                            z.extractall(DATA_DIR)
                    except zipfile.BadZipFile:
                        print(f"   ⚠ Corrupt zip for {info['name']}, deleting.")
                        os.remove(zip_path)
                        continue
                vpl_path = os.path.join(subdir, info["file"])
            else:
                vpl_path = os.path.join(DATA_DIR, info["subdir"], info["file"])
                if not os.path.exists(vpl_path):
                    print(f"   ⚠ {info['name']} missing – drop VPL into {os.path.dirname(vpl_path)}/")
                    continue

            if not os.path.exists(vpl_path):
                print(f"   ⚠ VPL file not found: {vpl_path}")
                continue

            print(f"Loading {info['name']}...")
            data = self.parse_vpl(vpl_path)
            loaded = 0
            for key, text in data.items():
                book_code = key[0].upper()
                if book_code in self.excluded_books:
                    continue
                self.verses[key][code] = text
                loaded += 1

                # Build corpus word frequency for hapax detection (original-language only)
                if code in ("gr", "heb"):
                    testament = "nt" if book_code in NT_BOOKS else "ot"
                    lang = "greek" if code == "gr" else "hebrew"
                    words = get_greek_words(text) if lang == "greek" else get_hebrew_words(text)
                    self.corpus_word_freq[testament].update(words)

            if loaded < len(data):
                print(f"   (excluded {len(data) - loaded} deuterocanonical verses)")

    def parse_vpl(self, file_path: str) -> Dict[tuple, str]:
        verses = {}
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                m = _VPL_RE.match(line)
                if not m:
                    continue
                book, ch, v, text = m.groups()
                text = text.strip()
                if len(text) <= 3 and (text.isdigit() or text.replace(":", "").replace(" ", "") == ""):
                    continue
                verses[(book.upper(), int(ch), int(v))] = text
        print(f"   Loaded {len(verses):,} verses")
        return verses

    # ── SBERT batch divergence (from Gemini) ─────────────────────────
    def compute_sbert_divergences(self, df: pd.DataFrame) -> List[float]:
        """Batch-compute semantic divergence using SBERT embeddings."""
        trans_cols = [c for c in ["en", "web", "asv", "sv"] if c in df.columns]
        if not self.sbert_model or len(trans_cols) < 2:
            return [0.0] * len(df)

        # Batch encode all translation columns
        embeddings = {}
        for col in trans_cols:
            texts = df[col].fillna("").tolist()
            print(f"   SBERT encoding {col.upper()}...")
            embeddings[col] = self.sbert_model.encode(texts, show_progress_bar=True,
                                                       convert_to_tensor=True)

        scores = []
        for idx in range(len(df)):
            valid_cols = [c for c in trans_cols if df.iloc[idx].get(c, "")]
            if len(valid_cols) < 2:
                scores.append(0.0)
                continue
            sims = []
            for i in range(len(valid_cols)):
                for j in range(i + 1, len(valid_cols)):
                    sim = sbert_util.cos_sim(
                        embeddings[valid_cols[i]][idx],
                        embeddings[valid_cols[j]][idx]
                    ).item()
                    sims.append(sim)
            scores.append(round((1 - statistics.mean(sims)) * 100, 1))
        return scores

    # ── Scoring engine ───────────────────────────────────────────────
    def compute_scores(self, row, semantic_div: float = 0.0):
        gr  = str(row.get("gr", "") or "")
        heb = str(row.get("heb", "") or "")
        lxx = str(row.get("lxx", "") or "")
        orig = gr or heb or lxx
        en_text = str(row.get("en", "") or "")
        book = str(row.get("book", ""))

        translations = [str(row.get(t, "")) for t in ["en", "web", "asv", "sv"]
                        if t in row and row[t]]

        # ── Log-ratio length metric (v12 new) ──
        en_len = max(1, len(translations[0].split())) if translations else 1
        orig_len = max(1, len(orig.split()))
        # Log-ratio: symmetric, stable across verse lengths
        length_ratio = round(abs(math.log2(max(orig_len, 1) / max(en_len, 1))) * 50, 1)
        length_ratio = min(length_ratio, 100.0)

        # ── Lexical ambiguity ──
        lang = detect_language(orig)
        if lang == "hebrew":
            words = get_hebrew_words(orig)
        elif lang == "greek":
            words = get_greek_words(orig)
        else:
            words = get_trans_words(orig)

        matched_roots = []
        for w in words:
            root = matches_polysemy(w, lang)
            if root and len(POLYSEMY.get(root, [])) > 1:
                matched_roots.append(root)
        amb_count = len(matched_roots)
        unique_roots = list(set(matched_roots))

        # ── Name-list filter ──
        if is_name_list(words, en_text):
            lex_ambiguity = 0.0
            name_list_flag = True
        else:
            sense_score = sum(len(POLYSEMY.get(r, [])) * 4 for r in matched_roots)
            lex_ambiguity = min(sense_score, 100)
            name_list_flag = False

        # ── Translation divergence ──
        if USE_SBERT:
            trans_div = semantic_div
        else:
            trans_div = 0.0
            if len(translations) > 1:
                sims = []
                for i in range(len(translations)):
                    for j in range(i + 1, len(translations)):
                        sims.append(token_jaccard(translations[i], translations[j]))
                trans_div = round((1 - statistics.mean(sims)) * 100, 1) if sims else 0.0

        # v12 stricter short-verse tiers (from Grok)
        if en_len < 7:
            trans_div = 0.0
        elif en_len < 12 and trans_div > 40:
            trans_div = 40.0

        # ── Morphological complexity ──
        ttr = type_token_ratio(words) * 100 if words else 0.0
        entropy = shannon_entropy(words) * 15
        morph_complexity = round(min((ttr * 0.5 + entropy * 0.5), 100), 1)

        # ── Hebrew ↔ LXX divergence ──
        heb_lxx_div = 0.0
        heb_lxx_poly_alignment = 0.0
        if heb and lxx:
            heb_lxx_div = 5.0
            heb_words = get_hebrew_words(heb)
            lxx_words = get_greek_words(lxx)
            heb_wc = len(heb_words)
            lxx_wc = len(lxx_words)

            # Structural divergence
            if heb_wc > 0 and lxx_wc > 0:
                structural_diff = abs(heb_wc - lxx_wc) / max(heb_wc, lxx_wc)
                heb_lxx_div += structural_diff * 25

            # Vocabulary richness divergence
            heb_vocab = len(set(heb_words))
            lxx_vocab = len(set(lxx_words))
            if heb_vocab > 0:
                vocab_diff = abs(heb_vocab - lxx_vocab) / max(1, heb_vocab)
                heb_lxx_div += vocab_diff * 20

            # v12 new: Cross-language polysemy alignment
            # Check if polysemous Hebrew roots have matching polysemous Greek in LXX
            heb_poly = set(matches_polysemy(w, "hebrew") for w in heb_words)
            lxx_poly = set(matches_polysemy(w, "greek") for w in lxx_words)
            heb_poly.discard(None)
            lxx_poly.discard(None)
            if heb_poly and lxx_poly:
                # Both have polysemous words: higher chance of interpretive divergence
                heb_lxx_poly_alignment = min(len(heb_poly) + len(lxx_poly), 10) * 2
                heb_lxx_div += heb_lxx_poly_alignment

            heb_lxx_div = round(min(heb_lxx_div, 50), 1)

        # ── Hapax legomena score (v12 new) ──
        testament = "nt" if book in NT_BOOKS else "ot"
        corpus_freq = self.corpus_word_freq.get(testament, Counter())
        hapax_count = 0
        if corpus_freq and words:
            hapax_count = sum(1 for w in words if corpus_freq.get(w, 0) == 1)
        hapax_score = min(hapax_count * 8, 40)  # max 40 points

        # ── Theological keyword boost ──
        theo_boost = 0.0
        theo_keywords_found = []
        weights = THEOLOGICAL_WEIGHTS_HEBREW if lang == "hebrew" else THEOLOGICAL_WEIGHTS_GREEK
        raw_weight_sum = 0.0
        for root in unique_roots:
            w = weights.get(root, 0)
            if w > 0:
                raw_weight_sum += w
                theo_keywords_found.append(f"{root}(+{w})")

        word_count = max(1, len(words))
        keyword_density = len(theo_keywords_found) / word_count
        theo_boost = min(raw_weight_sum * (1.0 + keyword_density * 5), 30.0)

        # ── Composite score ──
        is_ot_verse = bool(heb)
        theo_normalized = min(theo_boost * (100 / 30), 100)
        hapax_normalized = min(hapax_score * (100 / 40), 100)

        if is_ot_verse:
            composite = round(
                0.13 * length_ratio +
                0.22 * lex_ambiguity +
                0.10 * morph_complexity +
                0.18 * trans_div +
                0.15 * heb_lxx_div +       # v12: OT LXX boost (from Grok, raised from 13%)
                0.12 * theo_normalized +
                0.10 * hapax_normalized,    # v12 new
                1
            )
        else:
            composite = round(
                0.13 * length_ratio +
                0.24 * lex_ambiguity +
                0.10 * morph_complexity +
                0.23 * trans_div +
                0.05 * heb_lxx_div +
                0.13 * theo_normalized +
                0.12 * hapax_normalized,    # v12 new
                1
            )

        # ── Interpretation difficulty ──
        interp_difficulty = round(
            0.35 * lex_ambiguity +
            0.30 * trans_div +
            0.15 * morph_complexity +
            0.10 * hapax_normalized +       # v12: hapax contributes
            0.10 * theo_normalized,
            1
        )

        # ── Explanation engine ──
        reasons = []
        if name_list_flag:
            reasons.append("⚠ name-list / genealogy — polysemy suppressed")
        if amb_count > 0 and not name_list_flag:
            senses = []
            for r in unique_roots[:4]:
                meanings = POLYSEMY.get(r, [])
                senses.append(f"{r} ({'/'.join(meanings[:3])})")
            reasons.append(f"{amb_count} polysemous: {'; '.join(senses)}")
        if theo_keywords_found:
            reasons.append(f"theological keywords: {', '.join(theo_keywords_found[:5])}")
        if hapax_count > 0:
            reasons.append(f"{hapax_count} hapax legomen{'a' if hapax_count > 1 else 'on'} (rare words)")
        if length_ratio > 40:
            reasons.append(f"length mismatch (log-ratio {length_ratio:.0f})")
        if trans_div > 25:
            label = "semantic" if USE_SBERT else "4-way Jaccard"
            reasons.append(f"{label} divergence {trans_div}%")
        if morph_complexity > 60:
            reasons.append(f"morphological density (TTR={ttr:.0f}%, H={entropy:.1f})")
        if heb_lxx_div > 10:
            reasons.append(f"Hebrew↔LXX divergence {heb_lxx_div:.0f}%")
        if heb_lxx_poly_alignment > 0:
            reasons.append(f"cross-language polysemy alignment (+{heb_lxx_poly_alignment:.0f})")

        return {
            "length_ratio": length_ratio,
            "lex_ambiguity": lex_ambiguity,
            "morph_complexity": morph_complexity,
            "trans_divergence": trans_div,
            "heb_lxx_divergence": heb_lxx_div,
            "hapax_score": hapax_score,
            "theo_boost": theo_boost,
            "interp_difficulty": interp_difficulty,
            "composite": composite,
            "matched_roots": unique_roots,
            "name_list": name_list_flag,
            "reasons": reasons,
        }

    # ── Main analysis ────────────────────────────────────────────────
    def analyze(self, mode: str, excluded_books: Optional[Set[str]] = None,
                group: Optional[str] = None) -> dict:
        excluded = excluded_books or set()
        group_books = BOOK_GROUPS.get(group) if group else None
        rows = []
        for ref, texts in self.verses.items():
            book = ref[0]
            if book in excluded:
                continue
            if "en" not in texts:
                continue
            if mode == "nt" and book not in NT_BOOKS:
                continue
            if mode == "ot" and book in NT_BOOKS:
                continue
            if group_books and book not in group_books:
                continue
            if any(k in texts for k in ("gr", "heb", "lxx")):
                row = {"ref": f"{book} {ref[1]}:{ref[2]}", "book": book, **texts}
                rows.append(row)

        df = pd.DataFrame(rows).fillna("")
        if df.empty:
            print(f"   No verses found for mode={mode}, group={group}")
            return {}

        # SBERT batch processing (from Gemini)
        sbert_scores = [0.0] * len(df)
        if USE_SBERT:
            print(f"🧠 SBERT batch processing {len(df)} verses...")
            sbert_scores = self.compute_sbert_divergences(df)

        # Score each verse
        score_df = df.apply(
            lambda r: pd.Series(self.compute_scores(r, sbert_scores[r.name])),
            axis=1
        )
        df = pd.concat([df, score_df], axis=1)

        base_cols = ["ref", "book", "composite", "interp_difficulty",
                     "length_ratio", "lex_ambiguity", "morph_complexity",
                     "trans_divergence", "heb_lxx_divergence", "hapax_score",
                     "theo_boost", "matched_roots", "name_list", "reasons"]
        lang_cols = [c for c in ["gr", "heb", "lxx", "en", "web", "asv", "sv"]
                     if c in df.columns]
        final_cols = base_cols + lang_cols

        results = {}
        param_sets = {
            "overall_nuance_potential": "composite",
            "interpretation_difficulty": "interp_difficulty",
            "biggest_length_mismatch": "length_ratio",
            "highest_lexical_ambiguity": "lex_ambiguity",
            "morphology_complexity": "morph_complexity",
            "translation_divergence": "trans_divergence",
            "hapax_legomena": "hapax_score",
        }
        for name, sort_col in param_sets.items():
            top = df.nlargest(TOP_N, sort_col)
            results[name] = top[final_cols].to_dict(orient="records")

        results["_stats"] = {
            "total_verses": len(df),
            "avg_composite": round(df["composite"].mean(), 2),
            "avg_divergence": round(df["trans_divergence"].mean(), 2),
            "avg_lex_ambiguity": round(df["lex_ambiguity"].mean(), 2),
            "avg_interp_difficulty": round(df["interp_difficulty"].mean(), 2),
            "avg_hapax": round(df["hapax_score"].mean(), 2),
            "verses_with_polysemy": int((df["lex_ambiguity"] > 0).sum()),
            "verses_with_hapax": int((df["hapax_score"] > 0).sum()),
            "verses_with_heb_lxx": int((df["heb_lxx_divergence"] > 0).sum()),
            "verses_name_list_suppressed": int(df["name_list"].sum()),
            "verses_with_theo_boost": int((df["theo_boost"] > 0).sum()),
            "divergence_engine": "SBERT" if USE_SBERT else "Token Jaccard",
        }

        # ── SQLite export (from Gemini) ──
        if not args.no_sqlite:
            db_path = os.path.join(OUTPUT_DIR, f"nuance_{mode}.db")
            df_sql = df.copy()
            df_sql["reasons"] = df_sql["reasons"].apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
            df_sql["matched_roots"] = df_sql["matched_roots"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            try:
                with sqlite3.connect(db_path) as conn:
                    df_sql.to_sql("verses", conn, index=False, if_exists="replace")
                print(f"   💾 SQLite: {db_path}")
            except Exception as e:
                print(f"   ⚠ SQLite export failed: {e}")

        # ── CSV export (v12 new) ──
        if not args.no_csv:
            csv_path = os.path.join(OUTPUT_DIR, f"all_verses_{mode}.csv")
            csv_cols = ["ref", "book", "composite", "interp_difficulty",
                        "lex_ambiguity", "trans_divergence", "hapax_score",
                        "morph_complexity", "heb_lxx_divergence", "theo_boost"]
            try:
                df[csv_cols].sort_values("composite", ascending=False).to_csv(
                    csv_path, index=False, encoding="utf-8"
                )
                print(f"   📊 CSV: {csv_path}")
            except Exception as e:
                print(f"   ⚠ CSV export failed: {e}")

        return results


# ===================== RUN =====================
analyzer = BibleAnalyzer(excluded_books=EXCLUDED_BOOKS)
analyzer.load_all()

modes = (["nt", "ot"] if args.mode == "both"
         else [args.mode] if args.mode != "combined"
         else ["combined"])

for m in modes:
    label = f"{m.upper()}" + (f" [{args.canon}]" if args.canon != "all" else "") + \
            (f" ({args.group})" if args.group else "")
    print(f"\n🔍 Running {label} analysis...")
    res = analyzer.analyze(m, EXCLUDED_BOOKS, args.group)
    if not res:
        continue

    suffix = f"_{args.group}" if args.group else ""
    canon_tag = f"_{args.canon}" if args.canon != "all" else ""
    filename = f"{m}{canon_tag}{suffix}_analysis.json"
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    summary_name = f"summary_{m}{canon_tag}{suffix}.md"
    stats = res.get("_stats", {})
    with open(os.path.join(OUTPUT_DIR, summary_name), "w", encoding="utf-8") as f:
        f.write(f"# Bible Nuance Report v12.0 (Claude) – {label}\n\n")
        f.write(f"**Total verses**: {stats.get('total_verses', '?')}\n")
        f.write(f"**Divergence engine**: {stats.get('divergence_engine', '?')}\n")
        f.write(f"**Polysemy hits**: {stats.get('verses_with_polysemy', '?')}\n")
        f.write(f"**Hapax legomena verses**: {stats.get('verses_with_hapax', '?')}\n")
        f.write(f"**Theological boost**: {stats.get('verses_with_theo_boost', '?')}\n")
        f.write(f"**Name-lists suppressed**: {stats.get('verses_name_list_suppressed', '?')}\n")
        f.write(f"**Hebrew + LXX pairs**: {stats.get('verses_with_heb_lxx', '?')}\n")
        f.write(f"**Avg composite**: {stats.get('avg_composite', '?')}\n")
        f.write(f"**Avg divergence**: {stats.get('avg_divergence', '?')}%\n")
        f.write(f"**Avg hapax**: {stats.get('avg_hapax', '?')}\n")
        f.write(f"**Avg interpretation difficulty**: {stats.get('avg_interp_difficulty', '?')}\n\n")

        f.write("## Top verse overall (composite)\n")
        top = res.get("overall_nuance_potential", [{}])[0]
        f.write(f"**{top.get('ref', '?')}** — composite {top.get('composite', '?')}\n")
        for reason in top.get("reasons", []):
            f.write(f"  • {reason}\n")
        f.write("\n")

        f.write("## Top 10 most difficult to interpret\n")
        for r in res.get("interpretation_difficulty", [])[:10]:
            f.write(f"- **{r['ref']}** – difficulty {r['interp_difficulty']:.1f}")
            if r.get("theo_boost", 0) > 0:
                f.write(f" ⭐")
            if r.get("hapax_score", 0) > 0:
                f.write(f" 📖")
            f.write("\n")
            for reason in r.get("reasons", []):
                f.write(f"    • {reason}\n")

        f.write("\n## Top 10 by lexical ambiguity\n")
        for r in res.get("highest_lexical_ambiguity", [])[:10]:
            f.write(f"- **{r['ref']}** – score {r['lex_ambiguity']:.1f}\n")
            for reason in r.get("reasons", [])[:2]:
                f.write(f"    • {reason}\n")

        f.write("\n## Top 10 by translation divergence\n")
        for r in res.get("translation_divergence", [])[:10]:
            f.write(f"- **{r['ref']}** – divergence {r['trans_divergence']:.1f}%\n")
            if r.get("en"):
                snippet = r['en'][:90]
                f.write(f"    KJV: {snippet}{'...' if len(r['en']) > 90 else ''}\n")

        f.write("\n## Top 10 by hapax legomena\n")
        for r in res.get("hapax_legomena", [])[:10]:
            f.write(f"- **{r['ref']}** – hapax score {r['hapax_score']:.1f}\n")
            for reason in r.get("reasons", [])[:2]:
                f.write(f"    • {reason}\n")

    print(f"   ✅ {filename} + {summary_name}")

print(f"\n🎉 v12.0 (Claude) COMPLETE! Folder: {OUTPUT_DIR}/")
print("   New in v12.0:")
print("   • Hebrew suffix stripping (ים,ות,יו,הם — catches plurals & pronominals)")
print("   • Greek final-sigma normalization (ς→σ for consistent matching)")
print("   • Stricter short-verse tiers (<7 words: 0%, 7-11: max 40%)")
print("   • Hapax legomena detection (rare words → harder to translate)")
print("   • Log-ratio length metric (stable across verse lengths)")
print("   • Cross-language polysemy alignment (Hebrew↔LXX interpretive choices)")
print("   • SQLite database export (use --no-sqlite to skip)")
print("   • CSV flat export for spreadsheets (use --no-csv to skip)")
print("   • Optional SBERT semantic similarity (use --sbert)")
print(f"\n   Examples:")
print(f"     python bible.py --mode nt --group pauline --top 30")
print(f"     python bible.py --mode ot --canon protestant --group prophets")
print(f"     python bible.py --mode both --canon protestant --sbert")
print(f"     python bible.py --mode combined --no-sqlite --no-csv")

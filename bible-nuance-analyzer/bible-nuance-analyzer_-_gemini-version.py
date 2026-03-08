#!/usr/bin/env python3
"""
Bible Nuance Analyzer v12.0 (The NLP & SQLite Leap)
===================================================
Changes from v11.0:
  1. SEMANTIC TEXTUAL SIMILARITY (SBERT) — Replaced Token Jaccard with 
     Sentence-BERT embeddings. Measures true meaning divergence (cosine similarity) 
     rather than vocabulary overlap. Blazing fast batch-tensor processing.
  2. SQLITE DATABASE EXPORT — The script now generates a fully queryable 
     relational database ('nuance_database.db') for advanced cross-referencing.
  3. LINGUISTIC FALLACY FIX — Removed the flawed Hebrew↔LXX vocabulary size 
     comparison. Replaced with a baseline source-variant flag.
  4. ARCHITECTURAL REFACTOR — Decoupled the scoring engine to allow for 
     batch matrix operations on the GPU/CPU prior to row-level evaluation.
  5. All v11.0 Philological depth (Polysemy, Theo-Weights, Entropy) RETAINED.
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

# Attempt to load NLP libraries
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    SBERT_AVAILABLE = True
    print("✅ NLP Engine: sentence-transformers loaded.")
except ImportError:
    SBERT_AVAILABLE = False
    print("⚠ NLP Engine missing. pip install sentence-transformers for v12 semantic accuracy.")

# ===================== CONFIG & CONSTANTS =====================
DATA_DIR = "data"
TOP_N = 60

VERSIONS = {
    "gr":  {"name": "Greek_NT_RP",              "url": "https://ebible.org/Scriptures/grcmt_vpl.zip",     "subdir": "grcmt_vpl",     "file": "grcmt_vpl.txt",     "type": "nt"},
    "heb": {"name": "Hebrew_OT_WLC",            "url": "https://ebible.org/Scriptures/hbo_vpl.zip",      "subdir": "hbo_vpl",       "file": "hbo_vpl.txt",       "type": "ot"},
    "en":  {"name": "KJV",                      "url": "https://ebible.org/Scriptures/eng-kjv_vpl.zip",  "subdir": "eng-kjv_vpl",   "file": "eng-kjv_vpl.txt",   "type": "trans"},
    "web": {"name": "World English Bible",      "url": "https://ebible.org/Scriptures/eng-web_vpl.zip",  "subdir": "eng-web_vpl",   "file": "eng-web_vpl.txt",   "type": "trans"},
    "asv": {"name": "American Standard Version", "url": "https://ebible.org/Scriptures/eng-asv_vpl.zip", "subdir": "eng-asv_vpl",   "file": "eng-asv_vpl.txt",   "type": "trans"},
    "sv":  {"name": "Swedish_1917",                                                                       "subdir": "swe1917_vpl",   "file": "swe1917_vpl.txt",   "type": "trans"},
    "lxx": {"name": "Brenton Septuagint",       "url": "https://ebible.org/Scriptures/grcbrent_vpl.zip", "subdir": "grcbrent_vpl",  "file": "grcbrent_vpl.txt",  "type": "ot"},
}

NT_BOOKS = {
    "MAT","MRK","LUK","JHN","ACT",
    "ROM","1CO","2CO","GAL","EPH","PHP","COL",
    "1TH","2TH","1TI","2TI","TIT","PHM",
    "HEB","JAS","1PE","2PE","1JN","2JN","3JN","JUD","REV",
}

# ── Canon definitions ─────────────────────────────────────────────────────
APOCRYPHA_PROTESTANT = {
    "BAR","SIR","JDT","1MA","2MA","WIS","TOB",
    "1ES","2ES","MAN","PS2","LJE","S3Y","SUS",
    "BEL","DAG","ODE","EZA","5EZ","6EZ",
    "3MA","4MA","PSS","ESG","ADT",
    "GES","LAO","JUB","ENO","4ES","TAZ","JSA","JSB",
    "SST","DNT","BLT",
}
APOCRYPHA_CATHOLIC_EXTRA = {"3MA","4MA","PSS"}
APOCRYPHA_ORTHODOX_EXTRA = set()

def get_excluded_books(canon):
    if canon == "protestant": return APOCRYPHA_PROTESTANT
    if canon == "catholic": return APOCRYPHA_CATHOLIC_EXTRA
    if canon == "orthodox": return APOCRYPHA_ORTHODOX_EXTRA
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

# ===================== POLYSEMY DICTIONARY =====================
POLYSEMY = {
    # HEBREW (~100 roots)
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
    "מוفت": ["wonder", "portent", "sign", "miracle"],
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

    # GREEK (~250 lemmas)
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
    "ειρηνη":      ["peace", "harmony", "welfare", "wholleness"],
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
    "δυναμαι":     ["can", "be able", "be powerful"],
    "μελλω":       ["be about to", "intend", "be destined"],
    "αφιημι":      ["forgive", "leave", "permit", "let go", "abandon"],
    "αιρω":        ["take up", "carry", "remove", "take away"],
    "τιθημι":      ["put", "place", "set", "lay down", "appoint"],
    "ιστημι":      ["stand", "establish", "stop", "place"],
    "φερω":        ["bring", "carry", "bear", "produce", "endure"],
    "γεννω":       ["beget", "give birth", "produce", "cause"],
    "βαλλω":       ["throw", "cast", "put", "place"],
    "κρατεω":      ["seize", "hold", "possess", "arrest"],
    "ζητεω":       ["seek", "look for", "desire", "ask for"],
    "αιτεω":       ["ask", "request", "demand"],
    "κρινω":       ["judge", "decide", "condemn", "consider"],
    "σωζω":        ["save", "heal", "rescue", "preserve"],
    "κενοω":       ["empty", "make void", "make of no effect"],
    "κηρυσσω":     ["preach", "proclaim", "announce", "herald"],
    "προσευχομαι": ["pray", "intercede", "worship"],
    "δοκεω":       ["think", "seem", "suppose", "appear"],
    "φοβεομαι":    ["fear", "be afraid", "revere", "respect"],
    "χαιρω":       ["rejoice", "be glad", "greet"],
    "παρακαλεω":   ["encourage", "comfort", "exhort", "appeal", "beg"],
    "διδασκω":     ["teach", "instruct", "direct"],
    "αποκρινομαι": ["answer", "respond", "reply"],
    "μαρτυρεω":    ["testify", "witness", "affirm", "confirm"],
    "ομολογεω":    ["confess", "acknowledge", "profess", "agree"],
    "προσκυνεω":   ["worship", "bow down", "pay homage"],
    "δοξαζω":      ["glorify", "honor", "praise", "magnify"],
    "σταυροω":     ["crucify", "put to death"],
    "ονομα":       ["name", "reputation", "authority", "person"],
    "οδος":        ["way", "road", "path", "journey", "manner"],
    "εργον":       ["work", "deed", "action", "task"],
    "καρπος":      ["fruit", "crop", "result", "profit"],
    "σπερμα":      ["seed", "offspring", "descendant"],
    "λιθος":       ["stone", "rock", "jewel"],
    "οικος":       ["house", "household", "family", "temple"],
    "ναος":        ["temple", "sanctuary", "shrine"],
    "σωμα":        ["body", "substance", "reality", "slave"],
    "κεφαλη":      ["head", "leader", "authority", "source"],
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
    "αποστασια":   ["apostacy", "rebellion", "abandonment"],
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
    "τεχνη":       ["craft", "trade", "art"],
    "μαγεια":      ["sorcery", "magic"],
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
    "ικανος":      ["sufficient", "worthy", "able", "considerable"],
    "αξιος":       ["worthy", "deserving", "fitting"],
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
    "δικη":        ["justice", "punishment", "penalty"],
    "κληρος":      ["lot", "share", "inheritance", "portion"],
    "σκευος":      ["vessel", "instrument", "object", "body"],
    "στεφανος":    ["crown", "wreath", "prize"],
    "παιδεια":     ["discipline", "training", "education", "correction"],
    "μαστιξ":      ["whip", "scourge", "suffering", "affliction"],
    "λυτρον":      ["ransom", "redemption price"],
    "αντιλυτρον":  ["ransom", "corresponding price"],
    "μεσιτης":     ["mediator", "intermediary"],
    "αρχιερευς":   ["high priest", "chief priest"],
    "θυσιαστηριον": ["altar", "place of sacrifice"],
    "ιλαστηριον":  ["mercy seat", "propitiation", "place of atonement"],
    "περιτομη":    ["circumcision", "those circumcised"],
    "ακροβυστια":  ["uncircumcision", "Gentiles"],
    "κατακρινω":   ["condemn", "pass judgment on"],
    "ελογιζετο":   ["reckoned", "credited", "counted"],
    "δωρεαν":      ["freely", "without cause", "as a gift"],
    "ενεργεια":    ["working", "power", "activity", "energy"],
    "ευδοκια":     ["good pleasure", "will", "favor", "desire"],
    "παραπικρασμος":["provocation", "rebellion", "embitterment"],
    "σκληροκαρδια": ["hardness of heart", "stubbornness"],
    "ανακαινωσις": ["renewal", "renovation"],
    "μεταμορφοω":  ["transform", "transfigure", "change form"],
    "συσχηματιζω": ["conform", "fashion alike"],
    "αποθνησκω":   ["die", "perish", "be put to death"],
    "ζαω":         ["live", "be alive", "come to life"],
    "συζαω":       ["live with", "live together"],
    "συμβασιλευω": ["reign with", "co-reign"],
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
    "αιων":        ["age", "eternity", "world"],
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
    "αρχiερ":      ["high priest", "chief priest"],
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

# ── WEIGHTED theological keywords (~100 items) ──
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
    "πνευματ": 5, "πιστε": 5, "δικαιοσυν": 5, "χαριτ": 5, "αγαπ": 4,
    "αμαρτι": 4, "σωτηρι": 4, "βασιλει": 3, "αποκαλυψ": 4,
    "σαρκ": 4, "λογ": 4, "νομ": 3, "σταυρ": 4, "αναστα": 5,
    "διαθηκ": 5, "ιλασ": 5, "απολυτρωσ": 5, "λυτρ": 5, "μεσιτ": 4,
    "αρνι": 4, "μυστηρι": 3, "βαπτισ": 3, "σκανδαλ": 3,
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

def is_name_list(words, en_text=""):
    if not words or len(words) < 4: return False
    short_ratio = sum(1 for w in words if len(w) <= 3) / len(words)
    if en_text and re.search(r'\b(begat|son of|the sons of)\b', en_text, re.I) and short_ratio > 0.5: return True
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

        # SBERT Divergence
        trans_div = semantic_div
        if en_len < 5: trans_div = 0.0
        elif en_len < 12 and trans_div > 50: trans_div = 50.0

        # Hebrew-LXX baseline flag (v12 fix)
        heb_lxx_flag = 5.0 if heb and lxx else 0.0

        # Composite (v12 hybrid)
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

        print(f"🧠 Batch Processing {len(df)} verses...")
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

        # SQLITE EXPORT
        db_path = os.path.join(OUTPUT_DIR, f"nuance_v12_{mode}.db")
        df_sql = df.copy()
        df_sql['reasons'] = df_sql['reasons'].apply(lambda x: "; ".join(x))
        with sqlite3.connect(db_path) as conn: df_sql.to_sql("verses", conn, index=False, if_exists="replace")

        res = {}
        for label, col in {"overall_nuance_potential": "composite", "interpretation_difficulty": "interp_difficulty", "translation_divergence": "trans_divergence"}.items():
            res[label] = df.nlargest(TOP_N, col).to_dict(orient="records")
        
        res["_stats"] = {
            "total_verses": len(df), "avg_composite": round(df["composite"].mean(), 2),
            "avg_divergence": round(df["trans_divergence"].mean(), 2),
            "verses_with_polysemy": int((df["lex_ambiguity"] > 0).sum())
        }
        return res

# ===================== RUN =====================
parser = argparse.ArgumentParser(description="Bible Nuance Analyzer v12.0")
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

    with open(os.path.join(OUTPUT_DIR, f"summary_{m}.md"), "w", encoding="utf-8") as f:
        stats = res["_stats"]
        f.write(f"# Bible Nuance Report v12.0 – {m.upper()}\n\n")
        f.write(f"**Total**: {stats['total_verses']} | **Avg Composite**: {stats['avg_composite']} | **Avg Div**: {stats['avg_divergence']}%\n\n")
        f.write("## Top 10 Overall\n")
        for r in res["overall_nuance_potential"][:10]:
            f.write(f"- **{r['ref']}** ({r['composite']}): {'; '.join(r['reasons'])}\n")

print(f"\n🎉 v12.0 COMPLETE! Folder: {OUTPUT_DIR}/")

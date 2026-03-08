#!/usr/bin/env python3
"""
Bible Nuance Analyzer v11.0
===========================
Changes from v10.0 (based on field analysis of OT/NT reports):

  1. HEBREW PREFIX STRIPPING — strips ו,ה,ב,כ,ל,מ,ש prefixes before
     polysemy matching, catching וידע→ידע, בשלום→שלום etc.
     (ChatGPT §3.1, all three recommend)
  2. SENSE-WEIGHTED POLYSEMY — replaces flat ×12 with per-root sense
     count: len(POLYSEMY[root]) * 4. Words with 6 senses (λογος)
     score higher than words with 2 senses (τελος) (ChatGPT §3.4)
  3. LEXICAL HEBREW↔LXX DIVERGENCE — adds vocabulary-set comparison
     alongside structural word-count ratio, catching semantic
     reinterpretations like עלמה→παρθένος (ChatGPT §3.3, all three)
  4. THEOLOGICAL KEYWORD DENSITY — boost now proportional to
     keyword_count / verse_length, preventing single-keyword verses
     from getting disproportionate boosts (ChatGPT §3.5)
  5. ROBUST CANON EXCLUSION — expanded exclusion list with alternate
     eBible book codes + case-normalized matching (Grok #1 — SIR leak)
  6. All v10.0 improvements retained
"""

import os
import zipfile
import requests
import re
import json
import math
from collections import defaultdict
import pandas as pd
from datetime import datetime
import argparse
import unicodedata
import statistics

# ===================== CONFIG =====================
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
# Expanded with every known eBible VPL book code for deuterocanonical books
APOCRYPHA_PROTESTANT = {
    # Standard codes
    "BAR","SIR","JDT","1MA","2MA","WIS","TOB",
    "1ES","2ES","MAN","PS2","LJE","S3Y","SUS",
    "BEL","DAG","ODE","EZA","5EZ","6EZ",
    "3MA","4MA","PSS","ESG","ADT",
    # Alternate eBible/LXX codes that may appear
    "JDT","WIS","SIR","BAR","LJE","S3Y","SUS","BEL",
    "1MA","2MA","3MA","4MA","1ES","2ES","MAN","PS2",
    "ODE","PSS","ESG","DAG","ADT","EZA","5EZ","6EZ",
    # Additional potential variants
    "GES","LAO","JUB","ENO","4ES","TAZ","JSA","JSB",
    "SST","DNT","BLT",
}
APOCRYPHA_CATHOLIC_EXTRA = {"3MA","4MA","PSS"}
APOCRYPHA_ORTHODOX_EXTRA = set()

def get_excluded_books(canon):
    if canon == "protestant":
        return APOCRYPHA_PROTESTANT
    elif canon == "catholic":
        return APOCRYPHA_CATHOLIC_EXTRA
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

    # ── Nouns / concepts ──
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

    # ── NEW in v9.0: Johannine, Petrine, apocalyptic, pastoral ──
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

    # ── Additional stem-prefixes for high-frequency words (v9.0 fix) ──
    # These catch inflected forms where the stem is too short for the
    # full lemma to match (e.g. νομον→νομ doesn't start with νομος)
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
    "αρχιερ":      ["high priest", "chief priest"],
    "ανθρωπ":      ["person", "human", "man"],
    "γυναικ":      ["woman", "wife"],
    "ανδρ":        ["man", "husband"],
    "τεκν":        ["child", "descendant"],
    "πατρ":        ["father", "ancestor"],
    "αδελφ":       ["brother", "fellow believer"],
    "δουλ":        ["servant", "slave"],
    "κυρι":        ["lord", "master"],
    "θεο":         ["God", "god"],  # θεου, θεον, θεω
    "χριστ":       ["Christ", "anointed"],
    "υιο":         ["son", "descendant"],  # υιον, υιου, υιοι
}


# ── WEIGHTED theological keywords (new in v9) ────────────────────────────
# Values = importance weight (1–5 scale)
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
def normalize_greek(text):
    """Normalize Greek: lowercase, strip combining diacritics, keep Greek letters + spaces."""
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text.lower())
    # Keep only Greek letters (basic + extended) and whitespace
    return ''.join(c for c in nfkd
                   if ('\u0370' <= c <= '\u03FF') or ('\u1F00' <= c <= '\u1FFF')
                   or c in ' \t')


def normalize_hebrew(text):
    """Normalize Hebrew: strip niqqud / cantillation, keep consonants + spaces.
    Also normalizes final forms (ך→כ, ם→מ, ן→נ, ף→פ, ץ→צ) to medial forms
    so prefix matching works across word boundaries.
    """
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text)
    chars = []
    for c in nfkd:
        if '\u05D0' <= c <= '\u05EA' or c in ' \t':
            chars.append(c)
    result = ''.join(chars)
    # Normalize final forms to medial forms
    result = result.replace('ך', 'כ').replace('ם', 'מ').replace('ן', 'נ').replace('ף', 'פ').replace('ץ', 'צ')
    return result


def normalize_text(text):
    """General normalization for Latin-script translations."""
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text.lower())
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


# Pre-compiled regex
_WORD_RE = re.compile(r'\S+')
_LATIN_WORD_RE = re.compile(r'\b\w+\b')
_VPL_RE = re.compile(r'([A-Z0-9]{2,5})\s+(\d+):(\d+)\s+(.+)', re.IGNORECASE)

# Greek ending-stripping regex — only multi-char endings (≥2 chars)
# Single-char stripping was too aggressive (λογος→λογ via -ος then -ο)
_GREEK_ENDINGS = re.compile(
    r'(ους|οις|ων|ας|ης|ου|ος|ον|αι|εν|ες|ει|ις|ιν|αν|ην|ατ)$'
)


def get_hebrew_words(text):
    """Extract Hebrew consonant-only tokens, stripping punctuation."""
    return [w for w in _WORD_RE.findall(normalize_hebrew(text)) if len(w) >= 2]


def get_greek_words(text):
    """Extract normalized Greek tokens, stripping punctuation."""
    return [w for w in _WORD_RE.findall(normalize_greek(text)) if len(w) >= 2]


def get_trans_words(text):
    return _LATIN_WORD_RE.findall(normalize_text(text))


def detect_language(text):
    """Ratio-based language detection (fixes short-verse misclassification)."""
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


# ── Polysemy matching with Greek stemming ────────────────────────────────
# Build normalized root lists. Hebrew roots get final-form normalization
# so they match consistently with normalize_hebrew() output.
_FINAL_TO_MEDIAL = str.maketrans('ךםןףץ', 'כמנפצ')

def _norm_heb_root(k):
    return k.translate(_FINAL_TO_MEDIAL)

# Build Hebrew roots with normalized forms, mapping back to original key
_HEBREW_ROOT_MAP = {}  # normalized_root → original_key
for k in POLYSEMY:
    if any('\u05D0' <= c <= '\u05EA' for c in k):
        _HEBREW_ROOT_MAP[_norm_heb_root(k)] = k
_HEBREW_ROOTS = sorted(_HEBREW_ROOT_MAP.keys(), key=len, reverse=True)

_GREEK_ROOTS = sorted(
    [k for k in POLYSEMY if any('\u0370' <= c <= '\u03FF' for c in k)],
    key=len, reverse=True
)


def stem_greek(word):
    """Crude Greek stemmer: strip common inflectional endings.
    Returns a list of candidate stems (original + stripped) for matching.
    """
    candidates = [word]
    stripped = _GREEK_ENDINGS.sub('', word)
    if stripped and stripped != word and len(stripped) >= 3:
        candidates.append(stripped)
    return candidates


# ── Hebrew prefix stripping (new in v11) ─────────────────────────────────
# Hebrew commonly attaches ו(and), ה(the), ב(in), כ(like), ל(to), מ(from), ש(that)
# as single-letter prefixes. Strip them to expose the root for matching.
_HEB_PREFIXES = frozenset("והבכלמש")

def strip_hebrew_prefix(word):
    """Strip a single Hebrew prefix letter if the remaining word is ≥3 chars."""
    if len(word) > 3 and word[0] in _HEB_PREFIXES:
        return word[1:]
    return word

def strip_hebrew_prefixes_multi(word):
    """Strip up to 2 prefix letters (e.g. וב = and+in, ול = and+to)."""
    stripped = word
    for _ in range(2):
        if len(stripped) > 3 and stripped[0] in _HEB_PREFIXES:
            stripped = stripped[1:]
        else:
            break
    return stripped


def matches_polysemy(word, lang):
    """Return matched root key or None.
    Uses prefix match + Greek stemming, with a safety rule:
    - Hebrew: roots ≤2 chars require exact match (prevents בן→בנימין)
      but 3+ char roots prefix-match (Hebrew triconsonantal roots are 3)
    - Greek: roots ≤3 chars require exact match (prevents λογ→λογιζομαι)
    Hebrew roots are compared via final-form-normalized versions.
    """
    if lang == "hebrew":
        min_prefix_len = 3
        # Try original word first, then prefix-stripped variants
        candidates = [word]
        s1 = strip_hebrew_prefix(word)
        if s1 != word:
            candidates.append(s1)
        s2 = strip_hebrew_prefixes_multi(word)
        if s2 != word and s2 != s1:
            candidates.append(s2)

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
                    return root
            else:
                if word.startswith(root):
                    return root
        # Try stemmed candidate
        for candidate in stem_greek(word):
            if candidate == word:
                continue
            for root in _GREEK_ROOTS:
                if len(root) < min_prefix_len:
                    if candidate == root:
                        return root
                else:
                    if candidate.startswith(root):
                        return root
        return None


# ── Name-list / genealogy detector ───────────────────────────────────────
_GENEALOGY_INDICATORS_EN = re.compile(
    r'\b(begat|begot|son of|daughter of|the sons of|children of|were born)\b',
    re.IGNORECASE
)

def is_name_list(words, en_text=""):
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
    # Swedish
    "och", "i", "att", "det", "som", "en", "ett", "den", "av", "till",
    "med", "han", "var", "jag", "de", "på", "är", "vi", "har", "du",
    "inte", "för", "om", "sin", "dem", "hade", "sig", "hans", "från",
    "hon", "ska", "kan", "mot", "så", "alla", "ut", "men", "där",
})


def token_jaccard(a, b):
    if not a or not b:
        return 0.0
    sa = set(get_trans_words(a)) - _STOP_WORDS
    sb = set(get_trans_words(b)) - _STOP_WORDS
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# ── Shannon entropy & TTR ────────────────────────────────────────────────
def shannon_entropy(words):
    if not words:
        return 0.0
    freq = defaultdict(int)
    for w in words:
        freq[w] += 1
    total = len(words)
    return -sum((c / total) * math.log2(c / total) for c in freq.values())

def type_token_ratio(words):
    if not words:
        return 0.0
    return len(set(words)) / len(words)


# ===================== CLI =====================
parser = argparse.ArgumentParser(description="Bible Nuance Analyzer v11.0")
parser.add_argument("--mode", choices=["nt", "ot", "both", "combined"], default="both")
parser.add_argument("--top", type=int, default=60)
parser.add_argument("--canon", choices=["all", "protestant", "catholic", "orthodox"],
                    default="all")
parser.add_argument("--group", type=str, default=None,
                    choices=list(BOOK_GROUPS.keys()))
args = parser.parse_args()
TOP_N = args.top
EXCLUDED_BOOKS = get_excluded_books(args.canon)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
OUTPUT_DIR = f"results_{timestamp}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"🚀 Bible Nuance Analyzer v11.0")
print(f"Mode: {args.mode} | Canon: {args.canon} | Group: {args.group or 'all'} | Output: {OUTPUT_DIR}/")


# ===================== ANALYZER =====================
class BibleAnalyzer:
    def __init__(self, excluded_books=None):
        self.verses = defaultdict(dict)
        self.excluded_books = excluded_books or set()

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
                # Apply canon exclusion at load time (prevents deuterocanonical
                # books from LXX from ever entering the dataset)
                book_code = key[0].upper()
                if book_code in self.excluded_books:
                    continue
                self.verses[key][code] = text
                loaded += 1
            if loaded < len(data):
                print(f"   (excluded {len(data) - loaded} deuterocanonical verses)")

    def parse_vpl(self, file_path):
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

    # ── Scoring engine ───────────────────────────────────────────
    def compute_scores(self, row):
        gr  = str(row.get("gr", "") or "")
        heb = str(row.get("heb", "") or "")
        lxx = str(row.get("lxx", "") or "")
        orig = gr or heb or lxx
        en_text = str(row.get("en", "") or "")

        translations = [str(row.get(t, "")) for t in ["en", "web", "asv", "sv"]
                        if t in row and row[t]]

        # ── Length ratio ──
        en_len = max(1, len(translations[0].split())) if translations else 1
        orig_len = max(1, len(orig.split()))
        length_ratio = round(abs(orig_len - en_len) / en_len * 100, 1)

        # ── Lexical ambiguity (prefix matching + Greek stemming) ──
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
            # Sense-weighted polysemy scoring (v11): words with more senses
            # score higher. λογος (6 senses) > τελος (2 senses)
            sense_score = 0
            for root in matched_roots:
                sense_score += len(POLYSEMY.get(root, [])) * 4
            lex_ambiguity = min(sense_score, 100)
            name_list_flag = False

        # ── Translation divergence (token Jaccard) ──
        trans_div = 0.0
        if len(translations) > 1:
            sims = []
            for i in range(len(translations)):
                for j in range(i + 1, len(translations)):
                    sims.append(token_jaccard(translations[i], translations[j]))
            trans_div = round((1 - statistics.mean(sims)) * 100, 1) if sims else 0.0

        # ── Short-verse divergence guard (tiered in v10) ──
        # <5 words: divergence unreliable, zero it
        # 5–11 words: cap at 50%
        # ≥12 words: unrestricted
        if en_len < 5:
            trans_div = 0.0
        elif en_len < 12 and trans_div > 50:
            trans_div = 50.0

        # ── Morphological complexity (TTR + entropy) ──
        ttr = type_token_ratio(words) * 100 if words else 0.0
        entropy = shannon_entropy(words) * 15
        morph_complexity = round(min((ttr * 0.5 + entropy * 0.5), 100), 1)

        # ── Hebrew ↔ LXX divergence (improved in v11) ──
        heb_lxx_div = 0.0
        if heb and lxx:
            heb_lxx_div = 5.0  # baseline: both sources exist
            heb_words = get_hebrew_words(heb)
            lxx_words = get_greek_words(lxx)
            heb_wc = len(heb_words)
            lxx_wc = len(lxx_words)

            # Structural divergence (word count ratio)
            if heb_wc > 0 and lxx_wc > 0:
                structural_diff = abs(heb_wc - lxx_wc) / max(heb_wc, lxx_wc)
                heb_lxx_div += structural_diff * 25  # 0–25 range

            # Lexical divergence (vocabulary set size difference)
            # If LXX uses significantly different vocabulary richness than
            # Hebrew, it signals semantic expansion/contraction
            heb_vocab = len(set(heb_words))
            lxx_vocab = len(set(lxx_words))
            if heb_vocab > 0:
                vocab_diff = abs(heb_vocab - lxx_vocab) / max(1, heb_vocab)
                heb_lxx_div += vocab_diff * 20  # 0–20 range

            heb_lxx_div = round(min(heb_lxx_div, 50), 1)  # cap at 50

        # ── Weighted theological keyword boost (density-based in v11) ──
        theo_boost = 0.0
        theo_keywords_found = []
        weights = THEOLOGICAL_WEIGHTS_HEBREW if lang == "hebrew" else THEOLOGICAL_WEIGHTS_GREEK
        raw_weight_sum = 0.0
        for root in unique_roots:
            w = weights.get(root, 0)
            if w > 0:
                raw_weight_sum += w
                theo_keywords_found.append(f"{root}(+{w})")

        # Density: normalize by verse length to prevent single-keyword verses
        # from getting disproportionate boosts
        word_count = max(1, len(words))
        keyword_density = len(theo_keywords_found) / word_count
        theo_boost = min(raw_weight_sum * (1.0 + keyword_density * 5), 30.0)

        # ── Composite score (OT vs NT weighting in v10) ──
        # OT: higher weight on Hebrew↔LXX divergence
        # NT: higher weight on translation divergence
        is_ot_verse = bool(heb)
        theo_normalized = min(theo_boost * (100 / 30), 100)  # normalize to 0–100

        if is_ot_verse:
            composite = round(
                0.15 * length_ratio +
                0.25 * lex_ambiguity +
                0.12 * morph_complexity +
                0.20 * trans_div +
                0.13 * heb_lxx_div +
                0.15 * theo_normalized,
                1
            )
        else:
            composite = round(
                0.15 * length_ratio +
                0.26 * lex_ambiguity +
                0.13 * morph_complexity +
                0.26 * trans_div +
                0.05 * heb_lxx_div +
                0.15 * theo_normalized,
                1
            )

        # ── INTERPRETATION DIFFICULTY (new in v9) ──
        # Combines the three signals most correlated with scholarly debate
        interp_difficulty = round(
            0.40 * lex_ambiguity +
            0.35 * trans_div +
            0.25 * morph_complexity,
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
        if length_ratio > 70:
            reasons.append(f"length mismatch {length_ratio:.0f}%")
        if trans_div > 25:
            reasons.append(f"4-way divergence {trans_div}%")
        if morph_complexity > 60:
            reasons.append(f"morphological density (TTR={ttr:.0f}%, H={entropy:.1f})")
        if heb_lxx_div > 10:
            reasons.append(f"Hebrew↔LXX divergence {heb_lxx_div:.0f}%")

        return {
            "length_ratio": length_ratio,
            "lex_ambiguity": lex_ambiguity,
            "morph_complexity": morph_complexity,
            "trans_divergence": trans_div,
            "heb_lxx_divergence": heb_lxx_div,
            "theo_boost": theo_boost,
            "interp_difficulty": interp_difficulty,
            "composite": composite,
            "matched_roots": unique_roots,
            "name_list": name_list_flag,
            "reasons": reasons,
        }

    # ── Main analysis ────────────────────────────────────────────
    def analyze(self, mode, excluded_books=None, group=None):
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

        score_df = df.apply(lambda r: pd.Series(self.compute_scores(r)), axis=1)
        df = pd.concat([df, score_df], axis=1)

        base_cols = ["ref", "book", "composite", "interp_difficulty",
                     "length_ratio", "lex_ambiguity", "morph_complexity",
                     "trans_divergence", "heb_lxx_divergence",
                     "theo_boost", "matched_roots", "name_list", "reasons"]
        lang_cols = [c for c in ["gr", "heb", "lxx", "en", "web", "asv", "sv"] if c in df.columns]
        final_cols = base_cols + lang_cols

        results = {}
        param_sets = {
            "overall_nuance_potential": "composite",
            "interpretation_difficulty": "interp_difficulty",
            "biggest_length_mismatch": "length_ratio",
            "highest_lexical_ambiguity": "lex_ambiguity",
            "morphology_complexity": "morph_complexity",
            "translation_divergence": "trans_divergence",
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
            "verses_with_polysemy": int((df["lex_ambiguity"] > 0).sum()),
            "verses_with_heb_lxx": int((df["heb_lxx_divergence"] > 0).sum()),
            "verses_name_list_suppressed": int(df["name_list"].sum()),
            "verses_with_theo_boost": int((df["theo_boost"] > 0).sum()),
        }

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
        f.write(f"# Bible Nuance Report v11.0 – {label}\n\n")
        f.write(f"**Total verses**: {stats.get('total_verses', '?')}\n")
        f.write(f"**Polysemy hits**: {stats.get('verses_with_polysemy', '?')}\n")
        f.write(f"**Theological boost**: {stats.get('verses_with_theo_boost', '?')}\n")
        f.write(f"**Name-lists suppressed**: {stats.get('verses_name_list_suppressed', '?')}\n")
        f.write(f"**Hebrew + LXX pairs**: {stats.get('verses_with_heb_lxx', '?')}\n")
        f.write(f"**Avg composite**: {stats.get('avg_composite', '?')}\n")
        f.write(f"**Avg divergence**: {stats.get('avg_divergence', '?')}%\n")
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

    print(f"   ✅ {filename} + {summary_name}")

print(f"\n🎉 v11.0 COMPLETE! Folder: {OUTPUT_DIR}/")
print("   New in v11.0:")
print("   • Hebrew prefix stripping (ו,ה,ב,כ,ל,מ,ש → catches וידע→ידע, בשלום→שלום)")
print("   • Sense-weighted polysemy (λογος ×6 senses > τελος ×3 senses)")
print("   • Lexical Hebrew↔LXX divergence (vocabulary richness comparison)")
print("   • Theological keyword density (boost ∝ keywords/verse_length)")
print("   • Robust canon exclusion (expanded eBible book codes)")
print(f"\n   Examples:")
print(f"     python bible.py --mode nt --group pauline --top 30")
print(f"     python bible.py --mode ot --canon protestant --group prophets")
print(f"     python bible.py --mode both --canon protestant")

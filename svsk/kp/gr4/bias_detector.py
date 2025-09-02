import re
from collections import Counter

# Simple offline bias detector for minority language texts
def detect_bias(original_text, ai_translated_text, language="sami"):
    """Detects potential biases in AI translations by comparing original and translated texts."""
    # Normalize texts (lowercase, remove punctuation)
    original_words = re.findall(r'\w+', original_text.lower())
    translated_words = re.findall(r'\w+', ai_translated_text.lower())
    
    # Calculate word frequency differences
    orig_freq = Counter(original_words)
    trans_freq = Counter(translated_words)
    
    # Identify missing or altered terms (basic bias proxy)
    missing_terms = {word: count for word, count in orig_freq.items() if word not in trans_freq}
    added_terms = {word: count for word, count in trans_freq.items() if word not in orig_freq}
    
    # Calculate omission rate
    total_words = sum(orig_freq.values())
    omission_rate = sum(missing_terms.values()) / total_words if total_words > 0 else 0
    
    # Log results
    log = {
        "language": language,
        "omission_rate": round(omission_rate * 100, 2),
        "missing_terms": missing_terms,
        "added_terms": added_terms,
        "notes": "Check for cultural term loss (e.g., Sami-specific concepts)."
    }
    return log

# Example usage
if __name__ == "__main__":
    # Sample texts (replace with real Sami/Meänkieli data)
    original = "Sámi álbmot lea dehálaš kulturárbi."
    translated = "Sami folk är en viktig kulturarv."
    result = detect_bias(original, translated, "sami")
    print(f"Bias Detection Report: {result}")

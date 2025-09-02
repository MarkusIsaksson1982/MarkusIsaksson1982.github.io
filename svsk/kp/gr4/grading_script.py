import re
import json
from collections import Counter
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('stopwords', quiet=True)
except ImportError:
    # Fallback if NLTK not available
    pass

def grade_response(response_text, rubric_file="../common/language_grading_manifest.json", subject="Svenska"):
    """Further enhanced automated grading of text responses for Gy25 Svenska/SvA or Engelska based on rubric."""
    # Load rubric from manifest
    try:
        with open(rubric_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        rubric = next(s for s in manifest["subjects"] if s["name"] == subject)["rubric"]
    except FileNotFoundError:
        rubric = {
            "Språkriktighet & Retorik": "Nuanced, audience-adapted, sophisticated",
            "Källkritik & Analys": "Deep source critique; handles bias",
            "Innehåll & Reflektion": "Comprehensive theme understanding",
            "Overall (A)": "Independent, creative; 90-100% match"
        }

    # Normalize text
    words = re.findall(r'\w+', response_text.lower())
    word_count = len(words)
    unique_words = len(set(words))
    
    # Initialize scores (0-25 per dimension, total 100)
    scores = {"Språkriktighet & Retorik": 0, "Källkritik & Analys": 0, "Innehåll & Reflektion": 0, "Overall (A)": 0}
    
    # Språkriktighet & Retorik: Enhanced with stopword removal for diversity
    try:
        stop_words = set(stopwords.words('english' if subject == "Engelska" else 'swedish'))
        filtered_words = [w for w in words if w not in stop_words]
        vocabulary_diversity = len(set(filtered_words)) / len(filtered_words) if filtered_words else 0
    except NameError:
        vocabulary_diversity = unique_words / word_count if word_count > 0 else 0
    rhetorical_markers = len(re.findall(r'\b(therefore|however|moreover|consequently|for example|därför|dock|dessutom|konsekvent|till exempel)\b', response_text.lower()))
    if word_count >= 300 and rhetorical_markers >= 3 and vocabulary_diversity > 0.5:
        scores["Språkriktighet & Retorik"] = 25  # Full marks for rich, diverse language
    
    # Källkritik & Analys: Enhanced with bias keyword density
    citations = len(re.findall(r'https?://|source|källa|\[\d+\]', response_text))
    bias_terms = len(re.findall(r'\b(bias|equity|minority|cultural|ethics|bias|likvärdighet|minoritet|kulturell|etik)\b', response_text.lower()))
    bias_density = bias_terms / word_count if word_count > 0 else 0
    if citations >= 2 and bias_terms >= 3 and bias_density > 0.005:
        scores["Källkritik & Analys"] = 25  # Full marks for robust, dense critique
    
    # Innehåll & Reflektion: Enhanced with compound sentiment and Gy25 term depth
    try:
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(response_text)['compound']
        gy25_terms = len(re.findall(r'\b(digital|democracy|identity|proficiency|cross-cultural|digital|demokrati|identitet|kompetens|tvärs-kulturell)\b', response_text.lower()))
        if gy25_terms >= 4 and abs(sentiment) > 0.5 and gy25_terms / word_count > 0.01:  # Balanced sentiment and term density for nuance
            scores["Innehåll & Reflektion"] = 25  # Full marks for thematic/reflective depth
    except NameError:
        if gy25_terms >= 3:
            scores["Innehåll & Reflektion"] = 25
    
    # Overall: Aggregate and map to A (90-100%)
    total_score = sum(scores.values())
    scores["Overall (A)"] = 25 if total_score >= 90 else int(total_score * 25 / 100)
    
    # Feedback
    feedback = {
        "scores": scores,
        "total": total_score,
        "grade": "A" if total_score >= 90 else "B" if total_score >= 75 else "C",
        "notes": "Enhanced with stopword filtering, bias density, and Gy25 term depth. Log in ../common/grading_log.json."
    }
    
    return feedback

# Example usage
if __name__ == "__main__":
    # Sample text (replace with actual)
    sample_text = """
    Language identity is profoundly influenced by digital media... (full text)
    """
    result = grade_response(sample_text, subject="Engelska")
    print(f"Grading Result: {result}")

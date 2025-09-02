import re
import json
from collections import Counter
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    nltk.download('vader_lexicon', quiet=True)
except ImportError:
    # Fallback if NLTK not available (though it's in env)
    pass

def grade_response(response_text, rubric_file="../common/language_grading_manifest.json", subject="Svenska"):
    """Enhanced automated grading of text responses for Gy25 Svenska/SvA or Engelska based on rubric."""
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
    
    # Språkriktighet & Retorik: Check structure, style, diversity
    rhetorical_markers = len(re.findall(r'\b(therefore|however|moreover|consequently|for example|därför|dock|dessutom|konsekvent|till exempel)\b', response_text.lower()))
    vocabulary_diversity = unique_words / word_count if word_count > 0 else 0
    if word_count >= 300 and rhetorical_markers >= 3 and vocabulary_diversity > 0.5:
        scores["Språkriktighet & Retorik"] = 25  # Full marks for rich language
    
    # Källkritik & Analys: Count citations, bias terms
    citations = len(re.findall(r'https?://|source|källa|\[\d+\]', response_text))
    bias_terms = len(re.findall(r'\b(bias|equity|minority|cultural|ethics|bias|likvärdighet|minoritet|kulturell|etik)\b', response_text.lower()))
    if citations >= 2 and bias_terms >= 3:
        scores["Källkritik & Analys"] = 25  # Full marks for robust critique
    
    # Innehåll & Reflektion: Sentiment analysis for depth (using NLTK if available)
    try:
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(response_text)['compound']
        gy25_terms = len(re.findall(r'\b(digital|democracy|identity|proficiency|cross-cultural|digital|demokrati|identitet|kompetens|tvärs-kulturell)\b', response_text.lower()))
        if gy25_terms >= 4 and abs(sentiment) > 0.5:  # Balanced sentiment indicates nuance
            scores["Innehåll & Reflektion"] = 25  # Full marks for thematic/reflective depth
    except NameError:
        # Fallback without NLTK
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
        "notes": "Enhanced with vocabulary diversity and sentiment analysis. Log in ../common/grading_log.json."
    }
    
    return feedback

# Example usage
if __name__ == "__main__":
    # Sample text (replace with actual)
    sample_text = """
    AI is reshaping global education... (full text)
    """
    result = grade_response(sample_text, subject="Engelska")
    print(f"Grading Result: {result}")

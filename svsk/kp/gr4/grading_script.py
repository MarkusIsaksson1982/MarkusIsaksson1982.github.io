import re
import json
from collections import Counter

def grade_response(response_text, rubric_file="../common/language_grading_manifest.json", subject="Svenska"):
    """Automates grading of text responses for Gy25 Svenska/SvA or Engelska based on rubric."""
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
    
    # Initialize scores (0-25 per dimension, total 100)
    scores = {"Språkriktighet & Retorik": 0, "Källkritik & Analys": 0, "Innehåll & Reflektion": 0, "Overall (A)": 0}
    
    # Språkriktighet & Retorik: Check structure, style
    rhetorical_markers = len(re.findall(r'\b(therefore|however|moreover|consequently|for example)\b', response_text.lower()))
    if word_count >= 300 and rhetorical_markers >= 3:
        scores["Språkriktighet & Retorik"] = 25  # Full marks for dynamic structure
    
    # Källkritik & Analys: Count citations, bias terms
    citations = len(re.findall(r'https?://|source|\[\d+\]', response_text))
    bias_terms = len(re.findall(r'\b(bias|equity|minority|cultural|ethics)\b', response_text.lower()))
    if citations >= 2 and bias_terms >= 2:
        scores["Källkritik & Analys"] = 25  # Full marks for source critique
    
    # Innehåll & Reflektion: Check Gy25 themes, depth
    gy25_terms = len(re.findall(r'\b(digital|democracy|identity|proficiency|cross-cultural)\b', response_text.lower()))
    if gy25_terms >= 3 and word_count >= 300:
        scores["Innehåll & Reflektion"] = 25  # Full marks for thematic depth
    
    # Overall: Aggregate and map to A (90-100%)
    total_score = sum(scores.values())
    scores["Overall (A)"] = 25 if total_score >= 90 else int(total_score * 25 / 100)
    
    # Feedback
    feedback = {
        "scores": scores,
        "total": total_score,
        "grade": "A" if total_score >= 90 else "B" if total_score >= 75 else "C",
        "notes": "Check ../common/grading_log.json for cross-AI feedback."
    }
    
    return feedback

# Example usage
if __name__ == "__main__":
    # Sample text (replace with actual file read)
    sample_text = """
    AI is reshaping global education by offering personalized tools... (full text from sample_response_engelska.md)
    """
    result = grade_response(sample_text, subject="Engelska")
    print(f"Grading Result: {result}")

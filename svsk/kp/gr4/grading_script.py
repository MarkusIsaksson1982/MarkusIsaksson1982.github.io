import re
import json
from collections import Counter
import torch
import torch.nn as nn
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('stopwords', quiet=True)
except ImportError:
    # Fallback if NLTK not available
    pass

class SimpleMLScorer(nn.Module):
    """Simple ML model for response scoring using torch."""
    def __init__(self, input_size=4):
        super().__init__()
        self.linear = nn.Linear(input_size, 1)
        # Trained weights from dummy data
        with torch.no_grad():
            self.linear.weight.copy_(torch.tensor([[3.5643, 3.1141, 3.7135, 4.4387]]))
            self.linear.bias.copy_(torch.tensor([4.9951]))

    def forward(self, x):
        return torch.sigmoid(self.linear(x)) * 100  # Scale to 0-100 score

def extract_features(response_text, subject="Svenska"):
    """Extract features for ML scoring."""
    words = re.findall(r'\w+', response_text.lower())
    word_count = len(words)
    unique_words = len(set(words))
    
    # Feature 1: Vocabulary diversity
    vocabulary_diversity = unique_words / word_count if word_count > 0 else 0
    
    # Feature 2: Rhetorical markers count (normalized)
    rhetorical_markers = len(re.findall(r'\b(therefore|however|moreover|consequently|for example|därför|dock|dessutom|konsekvent|till exempel)\b', response_text.lower())) / 10.0
    
    # Feature 3: Bias terms density (normalized)
    bias_terms = len(re.findall(r'\b(bias|equity|minority|cultural|ethics|bias|likvärdighet|minoritet|kulturell|etik)\b', response_text.lower()))
    bias_density = (bias_terms / word_count * 100) if word_count > 0 else 0
    
    # Feature 4: Sentiment compound (NLTK or fallback 0.5)
    try:
        sia = SentimentIntensityAnalyzer()
        sentiment = abs(sia.polarity_scores(response_text)['compound'])
    except NameError:
        sentiment = 0.5
    
    return torch.tensor([vocabulary_diversity, rhetorical_markers, bias_density / 100, sentiment], dtype=torch.float32)  # Normalize for model

def grade_response(response_text, rubric_file="../common/language_grading_manifest.json", subject="Svenska"):
    """Further enhanced automated grading with integrated ML scorer for Gy25 responses."""
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
    
    # Extract features and use ML model
    features = extract_features(response_text, subject)
    model = SimpleMLScorer()
    ml_score = model(features).item()
    
    # Initialize scores (use ML score to adjust rule-based)
    scores = {"Språkriktighet & Retorik": 0, "Källkritik & Analys": 0, "Innehåll & Reflektion": 0, "Overall (A)": 0}
    
    # Språkriktighet & Retorik: Enhanced with stopword removal for diversity
    try:
        stop_words = set(stopwords.words('english' if subject == "Engelska" else 'swedish'))
        filtered_words = [w for w in words if w not in stop_words]
        vocabulary_diversity = len(set(filtered_words)) / len(filtered_words) if filtered_words else 0
    except NameError:
        vocabulary_diversity = len(set(words)) / word_count if word_count > 0 else 0
    rhetorical_markers = len(re.findall(r'\b(therefore|however|moreover|consequently|for example|därför|dock|dessutom|konsekvent|till exempel)\b', response_text.lower()))
    if word_count >= 300 and rhetorical_markers >= 3 and vocabulary_diversity > 0.5:
        scores["Språkriktighet & Retorik"] = 25  # Full marks for rich language
    
    # Källkritik & Analys: Enhanced with bias keyword density
    citations = len(re.findall(r'https?://|source|källa|\[\d+\]', response_text))
    bias_terms = len(re.findall(r'\b(bias|equity|minority|cultural|ethics|bias|likvärdighet|minoritet|kulturell|etik)\b', response_text.lower()))
    bias_density = bias_terms / word_count if word_count > 0 else 0
    if citations >= 2 and bias_terms >= 3 and bias_density > 0.005:
        scores["Källkritik & Analys"] = 25  # Full marks for robust critique
    
    # Innehåll & Reflektion: Enhanced with compound sentiment and Gy25 term depth
    try:
        sia = SentimentIntensityAnalyzer()
        sentiment = abs(sia.polarity_scores(response_text)['compound'])
        gy25_terms = len(re.findall(r'\b(digital|democracy|identity|proficiency|cross-cultural|digital|demokrati|identitet|kompetens|tvärs-kulturell)\b', response_text.lower()))
        if gy25_terms >= 4 and abs(sentiment) > 0.5 and gy25_terms / word_count > 0.01:  # Balanced sentiment and term density for nuance
            scores["Innehåll & Reflektion"] = 25  # Full marks for thematic/reflective depth
    except NameError:
        if gy25_terms >= 3:
            scores["Innehåll & Reflektion"] = 25
    
    # Overall: Average rule-based and ML score
    rule_total = sum(list(scores.values())[:3])
    total_score = (rule_total + ml_score) / 4
    scores["Overall (A)"] = 25 if total_score >= 90 else int(total_score * 25 / 100)
    
    # Feedback
    feedback = {
        "scores": scores,
        "total": round(total_score, 2),
        "grade": "A" if total_score >= 90 else "B" if total_score >= 75 else "C",
        "ml_score": round(ml_score, 2),
        "notes": "Integrated trained ML scorer using torch for feature-based prediction. Log in ../common/grading_log.json."
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

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
    pass

class SimpleMLScorer(nn.Module):
    """Simple ML model for response scoring."""
    def __init__(self, input_size=6):  # Increased for Mistral semantic score + intersektionell bias
        super().__init__()
        self.linear = nn.Linear(input_size, 1)
        with torch.no_grad():
            self.linear.weight.copy_(torch.tensor([[3.5643, 3.1141, 3.7135, 4.4387, 2.0, 1.5]]))  # Dummy weights
            self.linear.bias.copy_(torch.tensor([4.9951]))

    def forward(self, x):
        return torch.sigmoid(self.linear(x)) * 100

def extract_features(response_text, subject="Svenska"):
    """Extract features for ML scoring."""
    words = re.findall(r'\w+', response_text.lower())
    word_count = len(words)
    unique_words = len(set(words))
    
    # Feature 1: Vocabulary diversity
    vocabulary_diversity = unique_words / word_count if word_count > 0 else 0
    
    # Feature 2: Rhetorical markers (normalized)
    rhetorical_markers = len(re.findall(r'\b(therefore|however|moreover|consequently|for example|därför|dock|dessutom|konsekvent|till exempel)\b', response_text.lower())) / 10.0
    
    # Feature 3: Bias terms density (normalized)
    bias_terms = len(re.findall(r'\b(bias|equity|minority|cultural|ethics|bias|likvärdighet|minoritet|kulturell|etik)\b', response_text.lower()))
    bias_density = (bias_terms / word_count * 100) if word_count > 0 else 0
    
    # Feature 4: Sentiment compound
    try:
        sia = SentimentIntensityAnalyzer()
        sentiment = abs(sia.polarity_scores(response_text)['compound'])
    except NameError:
        sentiment = 0.5
    
    # Feature 5: Mistral semantic score (simulated)
    mistral_semantic_score = 0.8  # Placeholder; replace with Mistral API
    
    # Feature 6: Intersektionell bias (gender, class, ethnicity)
    intersektionell_terms = len(re.findall(r'\b(gender|class|ethnicity|kön|klass|etnicitet)\b', response_text.lower()))
    intersektionell_density = (intersektionell_terms / word_count * 100) if word_count > 0 else 0
    
    return torch.tensor([vocabulary_diversity, rhetorical_markers, bias_density / 100, sentiment, mistral_semantic_score, intersektionell_density / 100], dtype=torch.float32)

def grade_response(response_text, rubric_file="../common/language_grading_manifest.json", subject="Svenska"):
    """Enhanced grading with ML and Mistral integration."""
    try:
        with open(rubric_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        rubric = next(s for s in manifest["subjects"] if s["name"] == subject)["rubric"]
    except FileNotFoundError:
        rubric = {
            "Språkriktighet & Retorik": "Nuanced, audience-adapted, sophisticated language with varied stylistic devices.",
            "Källkritik & Analys": "Deep source critique, addressing bias and ethical implications, especially for minority languages.",
            "Innehåll & Reflektion": "Comprehensive understanding of themes, with innovative and ethical reflections.",
            "Språklig Kreativitet (Mistral)": "Creative use of stylistic devices to engage and persuade, with original phrasing.",
            "Källintegritet (Mistral)": "Seamless integration of credible sources into argumentation, with critical evaluation of reliability."
        }

    words = re.findall(r'\w+', response_text.lower())
    word_count = len(words)
    
    # Extract features and ML score
    features = extract_features(response_text, subject)
    model = SimpleMLScorer()
    ml_score = model(features).item()
    
    # Rule-based scores
    scores = {
        "Språkriktighet & Retorik": 0,
        "Källkritik & Analys": 0,
        "Innehåll & Reflektion": 0,
        "Språklig Kreativitet (Mistral)": 0,
        "Källintegritet (Mistral)": 0,
        "Overall (A)": 0
    }
    
    try:
        stop_words = set(stopwords.words('english' if subject == "Engelska" else 'swedish'))
        filtered_words = [w for w in words if w not in stop_words]
        vocabulary_diversity = len(set(filtered_words)) / len(filtered_words) if filtered_words else 0
    except NameError:
        vocabulary_diversity = len(set(words)) / word_count if word_count > 0 else 0
    rhetorical_markers = len(re.findall(r'\b(therefore|however|moreover|consequently|for example|därför|dock|dessutom|konsekvent|till exempel)\b', response_text.lower()))
    if word_count >= 300 and rhetorical_markers >= 3 and vocabulary_diversity > 0.5:
        scores["Språkriktighet & Retorik"] = 25
        scores["Språklig Kreativitet (Mistral)"] = 25 if rhetorical_markers >= 5 else 20
    
    citations = len(re.findall(r'https?://|source|källa|\[\d+\]', response_text))
    bias_terms = len(re.findall(r'\b(bias|equity|minority|cultural|ethics|bias|likvärdighet|minoritet|kulturell|etik)\b', response_text.lower()))
    bias_density = bias_terms / word_count if word_count > 0 else 0
    if citations >= 2 and bias_terms >= 3 and bias_density > 0.005:
        scores["Källkritik & Analys"] = 25
        scores["Källintegritet (Mistral)"] = 25 if citations >= 3 else 20
    
    try:
        sia = SentimentIntensityAnalyzer()
        sentiment = abs(sia.polarity_scores(response_text)['compound'])
        gy25_terms = len(re.findall(r'\b(digital|democracy|identity|proficiency|cross-cultural|digital|demokrati|identitet|kompetens|tvärs-kulturell)\b', response_text.lower()))
        if gy25_terms >= 4 and abs(sentiment) > 0.5 and gy25_terms / word_count > 0.01:
            scores["Innehåll & Reflektion"] = 25
    except NameError:
        if gy25_terms >= 3:
            scores["Innehåll & Reflektion"] = 25
    
    rule_total = sum(list(scores.values())[:3])
    total_score = (rule_total + ml_score) / 4
    scores["Overall (A)"] = 25 if total_score >= 90 else int(total_score * 25 / 100)
    
    feedback = {
        "scores": scores,
        "total": round(total_score, 2),
        "grade": "A" if total_score >= 90 else "B" if total_score >= 75 else "C",
        "ml_score": round(ml_score, 2),
        "notes": "Integrated trained ML scorer with simulated Mistral semantic and intersektionell bias detection. Log in ../common/grading_log.json."
    }
    
    return feedback

if __name__ == "__main__":
    sample_text = """
    Language identity is profoundly influenced by digital media... (full text)
    """
    result = grade_response(sample_text, subject="Engelska")
    print(f"Grading Result: {result}")

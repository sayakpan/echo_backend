import re
from textstat import flesch_reading_ease

def evaluate_text_basic(text):
    result = {
        "char_length": 0,
        "word_count": 0,
        "sentence_count": 0,
        "readability_score": 0,
        "diversity_score": 0,
        "composite_score": 0
    }

    if not text or not text.strip():
        return result

    text = text.strip()
    words = re.findall(r'\b\w+\b', text)
    sentences = re.split(r'[.!?]+', text)

    # Metrics
    result["char_length"] = len(text)
    result["word_count"] = len(words)
    result["sentence_count"] = len([s for s in sentences if s.strip()])
    result["readability_score"] = flesch_reading_ease(text)
    result["diversity_score"] = round(len(set(words)) / len(words) * 100, 1) if words else 0

    # Composite score (weighted mix of readability, diversity, dummy grammar penalty)
    composite = (
        min(result["readability_score"], 100) * 0.5 +
        (100 - min(result["grammar_issue_count"], 10) * 10) * 0.3 +
        min(result["diversity_score"], 100) * 0.2
    )
    result["composite_score"] = round(composite, 1)

    return result
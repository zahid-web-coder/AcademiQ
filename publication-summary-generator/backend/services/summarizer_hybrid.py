# services/summarizer_hybrid.py
from services.summarizer_extractive import extractive_summary
from services.summarizer_abstractive import abstractive_summary

def hybrid_summary(text: str, max_extractive_sentences: int = 5, abstractive_max_length: int = 150):
    """
    1) Extracts the top-N sentences (TextRank)
    2) Feeds them into T5 for a clean abstractive summary
    """
    if not text or not text.strip():
        return "Error: Empty text input."

    # Step 1: Extractive (cap sentences so T5 isn’t overloaded)
    extractive = extractive_summary(text, max_sentences=max_extractive_sentences)

    # Step 2: Abstractive (our T5 wrapper already handles truncation & CPU/GPU)
    final_sum = abstractive_summary(extractive, max_length=abstractive_max_length)
    return final_sum

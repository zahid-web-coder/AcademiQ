import nltk
import re
import math

# Ensure punkt is available for tokenization
nltk.download('punkt')
nltk.download('punkt_tab')

def sentence_tokenize(text):
    sentences = nltk.sent_tokenize(text)
    return [re.sub(r'\s+', ' ', sent.strip()) for sent in sentences if sent.strip()]

def word_tokenize(sentence):
    return [word.lower() for word in nltk.word_tokenize(sentence) if word.isalpha()]

def build_similarity_matrix(sentences):
    similarity_matrix = [[0 for _ in range(len(sentences))] for _ in range(len(sentences))]
    for idx1, sent1 in enumerate(sentences):
        for idx2, sent2 in enumerate(sentences):
            if idx1 != idx2:
                similarity_matrix[idx1][idx2] = sentence_similarity(sent1, sent2)
    return similarity_matrix

def sentence_similarity(sent1, sent2):
    words1 = set(word_tokenize(sent1))
    words2 = set(word_tokenize(sent2))
    if not words1 or not words2:
        return 0
    return len(words1.intersection(words2)) / (math.log(len(words1)+1) + math.log(len(words2)+1))

def textrank(sentences, top_n=3, d=0.85, min_diff=1e-5, steps=100):
    scores = [1.0] * len(sentences)
    sim_matrix = build_similarity_matrix(sentences)

    for _ in range(steps):
        new_scores = [1 - d + d * sum(
            (sim_matrix[j][i] / (sum(sim_matrix[j]) or 1)) * scores[j]
            for j in range(len(sentences)) if sim_matrix[j][i] != 0
        ) for i in range(len(sentences))]

        if sum(abs(new_scores[i] - scores[i]) for i in range(len(sentences))) <= min_diff:
            break
        scores = new_scores

    ranked_sentences = sorted(((scores[i], s, i) for i, s in enumerate(sentences)), reverse=True)
    selected = sorted(ranked_sentences[:top_n], key=lambda x: x[2])
    return " ".join(s for _, s, _ in selected)

def extractive_summary(text, max_sentences=5, top_n=None):
    """
    TextRank-based extractive summarizer.
    - max_sentences: backward compatibility (used in routes)
    - top_n: alternate param
    """
    try:
        sentences = sentence_tokenize(text)
        n = top_n if top_n is not None else max_sentences
        if len(sentences) <= n:
            return " ".join(sentences)
        return textrank(sentences, n)
    except Exception as e:
        return f"Error during summarization: {str(e)}"

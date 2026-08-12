from src.embeddings import encode_texts
from src.similarity import cosine_score


def test_semantic_similarity():

    texts = [
        "Python is a programming language.",
        "Python is a computer programming language."
    ]

    embeddings = encode_texts(texts)

    score = cosine_score(
        embeddings[0],
        embeddings[1]
    )

    assert score > 0.70
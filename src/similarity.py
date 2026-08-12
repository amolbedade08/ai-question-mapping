from sklearn.metrics.pairwise import (
    cosine_similarity as sklearn_cosine_similarity
)


def cosine_similarity(
    embedding_a,
    embedding_b
):
    """
    Calculate cosine similarity between
    two embeddings.
    """

    score = sklearn_cosine_similarity(
        [embedding_a],
        [embedding_b]
    )[0][0]

    return float(score)


def cosine_score(
    embedding_a,
    embedding_b
):
    """
    Backward-compatible function used by
    the existing similarity test.
    """

    return cosine_similarity(
        embedding_a,
        embedding_b
    )
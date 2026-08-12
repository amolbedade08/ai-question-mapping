from .embeddings import encode_texts
from .similarity import cosine_similarity


def map_chunks(
    model_chunks,
    student_chunks,
    top_k=1
):
    """
    Map each model-answer chunk to the most
    semantically similar student-answer chunks.

    Args:
        model_chunks: List of model answer chunks.
        student_chunks: List of student answer chunks.
        top_k: Number of student matches to retain.

    Returns:
        List of mapping results.
    """

    if not model_chunks or not student_chunks:
        return []

    model_embeddings = encode_texts(
        model_chunks
    )

    student_embeddings = encode_texts(
        student_chunks
    )

    mappings = []

    for model_index, model_embedding in enumerate(
        model_embeddings
    ):

        candidates = []

        for student_index, student_embedding in enumerate(
            student_embeddings
        ):

            score = cosine_similarity(
                model_embedding,
                student_embedding
            )

            candidates.append({
                "student_index": student_index,
                "student_text": student_chunks[
                    student_index
                ],
                "similarity": round(
                    score,
                    4
                )
            })

        candidates.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        mappings.append({
            "model_index": model_index,
            "model_text": model_chunks[
                model_index
            ],
            "matches": candidates[:top_k]
        })

    return mappings
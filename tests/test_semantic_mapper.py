from src.semantic_mapper import map_chunks


def test_map_chunks():

    model_chunks = [
        "Python is a programming language.",
        "Python supports object-oriented programming."
    ]

    student_chunks = [
        "Python is a high-level programming language.",
        "Python supports object-oriented and functional programming.",
        "The weather is pleasant today."
    ]

    result = map_chunks(
        model_chunks,
        student_chunks,
        top_k=1
    )

    assert len(result) == 2

    assert (
        result[0]["matches"][0]["similarity"] > 0.5
    )

    assert (
        result[1]["matches"][0]["similarity"] > 0.5
    )
from .embeddings import encode_texts
from .similarity import cosine_similarity


SUBJECT_THRESHOLD = 0.50


def extract_model_text(model_data):
    """Combine model question and answer for comparison."""

    if isinstance(model_data, str):
        return model_data

    if isinstance(model_data, dict):
        question = model_data.get("question", "")
        model_answer = model_data.get("model_answer", "")

        return f"{question}. {model_answer}".strip()

    return ""


def detect_subject(
    student_answers,
    dsa_model_answers,
    oop_model_answers
):
    """
    Detect whether a student's paper is DSA or OOP.

    Returns:
        {
            "subject": "DSA" / "OOP" / "UNKNOWN",
            "dsa_score": float,
            "oop_score": float
        }
    """

    if not student_answers:
        return {
            "subject": "UNKNOWN",
            "dsa_score": 0.0,
            "oop_score": 0.0
        }

    # --------------------------------------------------
    # Student text
    # --------------------------------------------------

    student_texts = [
        str(text)
        for text in student_answers.values()
        if text
    ]

    if not student_texts:
        return {
            "subject": "UNKNOWN",
            "dsa_score": 0.0,
            "oop_score": 0.0
        }

    # Encode student answers
    student_embeddings = encode_texts(student_texts)

    # --------------------------------------------------
    # DSA model embeddings
    # --------------------------------------------------

    dsa_texts = [
        extract_model_text(data)
        for data in dsa_model_answers.values()
    ]

    dsa_embeddings = encode_texts(dsa_texts)

    # --------------------------------------------------
    # OOP model embeddings
    # --------------------------------------------------

    oop_texts = [
        extract_model_text(data)
        for data in oop_model_answers.values()
    ]

    oop_embeddings = encode_texts(oop_texts)

    # --------------------------------------------------
    # Compare student against each subject
    # --------------------------------------------------

    dsa_scores = []
    oop_scores = []

    for student_embedding in student_embeddings:

        # Best DSA similarity for this student question
        dsa_best = max(
            cosine_similarity(
                student_embedding,
                model_embedding
            )
            for model_embedding in dsa_embeddings
        )

        # Best OOP similarity for this student question
        oop_best = max(
            cosine_similarity(
                student_embedding,
                model_embedding
            )
            for model_embedding in oop_embeddings
        )

        dsa_scores.append(float(dsa_best))
        oop_scores.append(float(oop_best))

    # Average best-question similarity
    dsa_score = sum(dsa_scores) / len(dsa_scores)
    oop_score = sum(oop_scores) / len(oop_scores)

    # --------------------------------------------------
    # Subject decision
    # --------------------------------------------------

    if (
        dsa_score >= SUBJECT_THRESHOLD
        and dsa_score > oop_score
    ):
        subject = "DSA"

    elif (
        oop_score >= SUBJECT_THRESHOLD
        and oop_score > dsa_score
    ):
        subject = "OOP"

    else:
        subject = "UNKNOWN"

    print()
    print("SUBJECT DETECTION")
    print(f"DSA score : {dsa_score:.4f}")
    print(f"OOP score : {oop_score:.4f}")
    print(f"Detected  : {subject}")

    return {
        "subject": subject,
        "dsa_score": round(dsa_score, 4),
        "oop_score": round(oop_score, 4)
    }
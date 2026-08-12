import re

from .embeddings import encode_texts
from .similarity import cosine_similarity


# Thresholds for question mapping.
#
# When question numbers agree, we can accept a slightly
# lower semantic similarity because the OCR/question number
# provides an additional signal.
SAME_NUMBER_THRESHOLD = 0.60

GENERAL_THRESHOLD = 0.70


def normalize_question_id(question_id):
    """
    Normalize question identifiers.

    Examples:
        q1          -> Q1
        Q 1         -> Q1
        Q.1         -> Q1
        Question 1  -> Q1
        1           -> Q1
    """

    value = str(question_id).strip().upper()

    value = value.replace(" ", "")
    value = value.replace(".", "")
    value = value.replace(":", "")

    if value.startswith("QUESTION"):
        value = (
            "Q"
            + value[len("QUESTION"):]
        )

    if value.isdigit():
        value = "Q" + value

    return value


def get_question_number(question_id):
    """
    Extract numeric question number.

    Examples:
        Q1 -> 1
        Q2 -> 2
        Q1991 -> 1991
    """

    normalized = normalize_question_id(
        question_id
    )

    match = re.fullmatch(
        r"Q(\d+)",
        normalized
    )

    if not match:
        return None

    return int(match.group(1))


def extract_model_text(model_data):
    """
    Combine model question and model answer
    for semantic comparison.
    """

    if isinstance(model_data, str):
        return model_data

    if isinstance(model_data, dict):

        question = model_data.get(
            "question",
            ""
        )

        model_answer = model_data.get(
            "model_answer",
            ""
        )

        return (
            f"{question}. "
            f"{model_answer}"
        ).strip()

    return ""


def map_questions(
    student_answers,
    model_answers
):
    """
    Map each student question to a model question.

    Mapping uses:

        1. Semantic similarity
        2. Question-number agreement

    Question number alone is never sufficient.
    """

    if not student_answers:
        return {}

    if not model_answers:
        return {}

    # -------------------------------------------------
    # Prepare model questions
    # -------------------------------------------------

    model_ids = list(
        model_answers.keys()
    )

    model_texts = [
        extract_model_text(
            model_answers[model_id]
        )
        for model_id in model_ids
    ]

    # Generate model embeddings once.
    model_embeddings = encode_texts(
        model_texts
    )

    results = {}

    # -------------------------------------------------
    # Process every student question
    # -------------------------------------------------

    for student_id, student_text in (
        student_answers.items()
    ):

        if not student_text:

            results[student_id] = {
                "matched_model_question": None,
                "best_candidate": None,
                "similarity": 0.0,
                "status": "empty_answer",
                "candidates": []
            }

            continue

        # Student embedding.
        student_embedding = encode_texts(
            [student_text]
        )[0]

        student_number = get_question_number(
            student_id
        )

        candidates = []

        # -------------------------------------------------
        # Compare against EVERY model question
        # -------------------------------------------------

        for index, model_id in enumerate(
            model_ids
        ):

            model_embedding = (
                model_embeddings[index]
            )

            score = cosine_similarity(
                student_embedding,
                model_embedding
            )

            model_number = get_question_number(
                model_id
            )

            number_match = (
                student_number is not None
                and model_number is not None
                and student_number == model_number
            )

            candidates.append({
                "model_question": model_id,
                "similarity": round(
                    float(score),
                    4
                ),
                "number_match": number_match
            })

        # -------------------------------------------------
        # Sort by semantic similarity
        # -------------------------------------------------

        candidates.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        best = candidates[0]

        best_score = best["similarity"]
        number_match = best["number_match"]

        # -------------------------------------------------
        # Determine threshold
        # -------------------------------------------------

        if number_match:

            required_threshold = (
                SAME_NUMBER_THRESHOLD
            )

        else:

            required_threshold = (
                GENERAL_THRESHOLD
            )

        # -------------------------------------------------
        # Decide mapping
        # -------------------------------------------------

        if best_score >= required_threshold:

            matched_question = (
                best["model_question"]
            )

            status = "matched"

        else:

            matched_question = None

            status = "unmatched"

        # -------------------------------------------------
        # Debug information
        # -------------------------------------------------

        print(
            f"Student {student_id} -> "
            f"Best Model {best['model_question']} | "
            f"similarity={best_score:.4f} | "
            f"number_match={number_match} | "
            f"threshold={required_threshold:.2f} | "
            f"status={status}"
        )

        # -------------------------------------------------
        # Save result
        # -------------------------------------------------

        results[student_id] = {

            "matched_model_question":
                matched_question,

            "best_candidate":
                best["model_question"],

            "similarity":
                best_score,

            "number_match":
                number_match,

            "threshold_used":
                required_threshold,

            "status":
                status,

            "candidates":
                candidates
        }

    return results
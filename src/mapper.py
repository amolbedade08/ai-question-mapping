import re

from .embeddings import encode_texts
from .similarity import cosine_similarity


# ---------------------------------------------------------
# Mapping thresholds
# ---------------------------------------------------------

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
        value = "Q" + value[len("QUESTION"):]

    if value.isdigit():
        value = "Q" + value

    return value


def get_question_number(question_id):
    """
    Extract numeric question number.

    Q1 -> 1
    Q2 -> 2
    """

    normalized = normalize_question_id(question_id)

    match = re.fullmatch(r"Q(\d+)", normalized)

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

        return f"{question}. {model_answer}".strip()

    return ""


def map_questions(student_answers, model_answers):
    """
    Map each student question to the corresponding model question.

    Strategy:

    1. Calculate semantic similarity against all model questions.
    2. If the same question number exists, evaluate that candidate
       first.
    3. Same-number candidate must pass SAME_NUMBER_THRESHOLD.
    4. If same-number candidate does not pass, allow a semantic
       fallback only when GENERAL_THRESHOLD is reached.
    5. Never force an unrelated question to match.
    """

    if not student_answers:
        return {}

    if not model_answers:
        return {}

    # ---------------------------------------------------------
    # Prepare model questions
    # ---------------------------------------------------------

    model_ids = list(model_answers.keys())

    model_texts = [
        extract_model_text(model_answers[model_id])
        for model_id in model_ids
    ]

    # Generate model embeddings once.
    model_embeddings = encode_texts(model_texts)

    results = {}

    # ---------------------------------------------------------
    # Process each student question
    # ---------------------------------------------------------

    for student_id, student_text in student_answers.items():

        if not student_text:

            results[student_id] = {
                "matched_model_question": None,
                "best_candidate": None,
                "similarity": 0.0,
                "number_match": False,
                "threshold_used": 0.0,
                "status": "empty_answer",
                "candidates": []
            }

            continue

        # -----------------------------------------------------
        # Student embedding
        # -----------------------------------------------------

        student_embedding = encode_texts(
            [student_text]
        )[0]

        student_number = get_question_number(student_id)

        candidates = []

        # -----------------------------------------------------
        # Compare against every model question
        # -----------------------------------------------------

        for index, model_id in enumerate(model_ids):

            score = cosine_similarity(
                student_embedding,
                model_embeddings[index]
            )

            model_number = get_question_number(model_id)

            number_match = (
                student_number is not None
                and model_number is not None
                and student_number == model_number
            )

            candidates.append({
                "model_question": model_id,
                "similarity": round(float(score), 4),
                "number_match": number_match
            })

        # -----------------------------------------------------
        # Sort semantic candidates
        # -----------------------------------------------------

        candidates.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        best_semantic = candidates[0]

        # -----------------------------------------------------
        # Find same-number candidate
        # -----------------------------------------------------

        same_number_candidates = [
            candidate
            for candidate in candidates
            if candidate["number_match"]
        ]

        matched_question = None
        selected_candidate = best_semantic
        required_threshold = GENERAL_THRESHOLD
        status = "unmatched"

        # -----------------------------------------------------
        # CASE 1:
        # Same question number exists
        # -----------------------------------------------------

        if same_number_candidates:

            same_number_candidate = same_number_candidates[0]

            same_number_score = (
                same_number_candidate["similarity"]
            )

            if same_number_score >= SAME_NUMBER_THRESHOLD:

                matched_question = (
                    same_number_candidate["model_question"]
                )

                selected_candidate = same_number_candidate

                required_threshold = SAME_NUMBER_THRESHOLD

                status = "matched"

            else:

                # Same number exists, but semantic evidence
                # is too weak.
                #
                # Do NOT force a match.
                matched_question = None

                selected_candidate = same_number_candidate

                required_threshold = SAME_NUMBER_THRESHOLD

                status = "unmatched"

        # -----------------------------------------------------
        # CASE 2:
        # No same-number model question exists
        # -----------------------------------------------------

        else:

            if (
                best_semantic["similarity"]
                >= GENERAL_THRESHOLD
            ):

                matched_question = (
                    best_semantic["model_question"]
                )

                selected_candidate = best_semantic

                required_threshold = GENERAL_THRESHOLD

                status = "matched"

            else:

                matched_question = None

                selected_candidate = best_semantic

                required_threshold = GENERAL_THRESHOLD

                status = "unmatched"

        # -----------------------------------------------------
        # Debug output
        # -----------------------------------------------------

        print(
            f"Student {student_id} -> "
            f"Best Model {selected_candidate['model_question']} | "
            f"similarity={selected_candidate['similarity']:.4f} | "
            f"number_match={selected_candidate['number_match']} | "
            f"threshold={required_threshold:.2f} | "
            f"status={status}"
        )

        # -----------------------------------------------------
        # Save result
        # -----------------------------------------------------

        results[student_id] = {

            "matched_model_question":
                matched_question,

            "best_candidate":
                selected_candidate["model_question"],

            "similarity":
                selected_candidate["similarity"],

            "number_match":
                selected_candidate["number_match"],

            "threshold_used":
                required_threshold,

            "status":
                status,

            "candidates":
                candidates
        }

    return results  
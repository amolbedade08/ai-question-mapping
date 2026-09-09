import json
import ollama


MODEL_NAME = "llama3.2"
MAX_MARKS_PER_QUESTION = 10


def extract_json(text):
    """Extract JSON from Ollama response."""

    text = text.strip()

    if "```json" in text:
        text = text.split("```json", 1)[1]
        text = text.split("```", 1)[0].strip()

    elif "```" in text:
        text = text.split("```", 1)[1]
        text = text.split("```", 1)[0].strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def get_criterion_name(criterion):
    """Get criterion text from rubric."""

    return str(
        criterion.get("criterion")
        or criterion.get("description")
        or criterion.get("name")
        or ""
    ).strip()


def get_criterion_marks(criterion):
    """Get maximum marks for a criterion."""

    value = criterion.get(
        "marks",
        criterion.get("max_marks", 0)
    )

    try:
        return max(0, int(value))
    except (ValueError, TypeError):
        return 0


def normalize_marks(value, max_marks):
    """Ensure awarded marks stay within criterion limits."""

    try:
        marks = float(value)
    except (ValueError, TypeError):
        marks = 0.0

    marks = max(0.0, min(marks, float(max_marks)))

    # Store whole numbers when possible
    if marks.is_integer():
        return int(marks)

    return round(marks, 2)


def evaluate_answer(
    question_id,
    student_answer,
    rubric
):
    """
    Evaluate one student answer against one rubric.
    """

    criteria = rubric.get("criteria", [])

    if not criteria:
        return {
            "question_id": question_id,
            "criteria": [],
            "total_marks": 0,
            "max_marks": 0,
            "evaluation_status": "no_rubric"
        }

    # Empty student answer
    if not student_answer or not str(student_answer).strip():

        empty_criteria = []

        for criterion in criteria:
            criterion_name = get_criterion_name(criterion)
            max_marks = get_criterion_marks(criterion)

            empty_criteria.append({
                "criterion": criterion_name,
                "marks_awarded": 0,
                "max_marks": max_marks,
                "reason": "No answer provided."
            })

        return {
            "question_id": question_id,
            "criteria": empty_criteria,
            "total_marks": 0,
            "max_marks": sum(
                item["max_marks"]
                for item in empty_criteria
            ),
            "evaluation_status": "empty_answer"
        }

    rubric_text = json.dumps(
        criteria,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are an expert university examiner.

Evaluate the student's answer using ONLY the supplied grading rubric.

Question ID:
{question_id}

Student Answer:
{student_answer}

Grading Rubric:
{rubric_text}

Rules:

1. Evaluate every rubric criterion.
2. Do not invent additional criteria.
3. Award marks only for content demonstrated in the student answer.
4. Partial marks are allowed.
5. Do not award more than the maximum marks for a criterion.
6. Do not give marks simply because something appears in the rubric.
7. The student's answer must demonstrate the concept.
8. Give a short reason for the marks awarded.
9. Return ONLY valid JSON.
10. Keep the criterion text exactly as supplied.

Use exactly this format:

{{
    "criteria": [
        {{
            "criterion": "criterion text",
            "marks_awarded": 2,
            "max_marks": 2,
            "reason": "Short explanation."
        }}
    ]
}}
"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json",
            options={
                "temperature": 0
            }
        )

        content = response["message"]["content"]

    except Exception as error:

        print(
            f"[ERROR] Ollama evaluation failed "
            f"for {question_id}: {error}"
        )

        return {
            "question_id": question_id,
            "criteria": [],
            "total_marks": 0,
            "max_marks": sum(
                get_criterion_marks(item)
                for item in criteria
            ),
            "evaluation_status": "ollama_error"
        }

    evaluation_data = extract_json(content)

    if not evaluation_data:
        print(
            f"[ERROR] Invalid evaluation JSON "
            f"for {question_id}"
        )

        return {
            "question_id": question_id,
            "criteria": [],
            "total_marks": 0,
            "max_marks": sum(
                get_criterion_marks(item)
                for item in criteria
            ),
            "evaluation_status": "invalid_response"
        }

    returned_criteria = evaluation_data.get(
        "criteria",
        []
    )

    if not isinstance(returned_criteria, list):
        returned_criteria = []

    # Map LLM response by criterion name
    returned_by_name = {}

    for item in returned_criteria:

        if not isinstance(item, dict):
            continue

        name = get_criterion_name(item)

        if name:
            returned_by_name[name.lower()] = item

    final_criteria = []

    for rubric_criterion in criteria:

        criterion_name = get_criterion_name(
            rubric_criterion
        )

        max_marks = get_criterion_marks(
            rubric_criterion
        )

        llm_result = returned_by_name.get(
            criterion_name.lower()
        )

        if llm_result is None:

            marks_awarded = 0
            reason = "Criterion was not addressed."

        else:

            marks_awarded = normalize_marks(
                llm_result.get("marks_awarded", 0),
                max_marks
            )

            reason = str(
                llm_result.get("reason", "")
            ).strip()

            if not reason:
                reason = "No reason provided."

        final_criteria.append({
            "criterion": criterion_name,
            "marks_awarded": marks_awarded,
            "max_marks": max_marks,
            "reason": reason
        })

    total_marks = sum(
        item["marks_awarded"]
        for item in final_criteria
    )

    max_marks = sum(
        item["max_marks"]
        for item in final_criteria
    )

    # Final Python safety check
    total_marks = min(
        total_marks,
        MAX_MARKS_PER_QUESTION
    )

    return {
        "question_id": question_id,
        "criteria": final_criteria,
        "total_marks": total_marks,
        "max_marks": max_marks,
        "evaluation_status": "evaluated"
    }


def evaluate_student_answers(
    student_id,
    student_answers,
    mappings,
    rubrics
):
    """Evaluate all matched student answers."""

    evaluations = []

    for student_question, mapping in mappings.items():

        if mapping.get("status") != "matched":
            continue

        model_question = mapping.get(
            "matched_model_question"
        )

        if not model_question:
            continue

        rubric = rubrics.get(
            student_question
        )

        if not rubric:
            print(
                f"[WARNING] No rubric found for "
                f"{student_question}"
            )
            continue

        student_answer = student_answers.get(
            student_question,
            ""
        )

        print()
        print(
            f"Evaluating {student_question} "
            f"against rubric..."
        )

        evaluation = evaluate_answer(
            model_question,
            student_answer,
            rubric
        )

        evaluation["student_question"] = (
            student_question
        )

        evaluation["matched_model_question"] = (
            model_question
        )

        evaluations.append(evaluation)

        print(
            f"[EVALUATION] {student_question}: "
            f"{evaluation['total_marks']}/"
            f"{evaluation['max_marks']}"
        )

    total_marks = sum(
        item["total_marks"]
        for item in evaluations
    )

    max_marks = sum(
        item["max_marks"]
        for item in evaluations
    )

    return {
        "student_id": student_id,
        "evaluations": evaluations,
        "total_marks": total_marks,
        "max_marks": max_marks
    }
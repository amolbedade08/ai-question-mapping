import json
from pathlib import Path
import ollama

from .database import save_rubric


MODEL_NAME = "llama3.2"
TOTAL_MARKS = 10

DSA_MODEL_FILE = Path("model_answers/model_answers.json")
OOP_MODEL_FILE = Path("model_answers/oop_model_answers.json")

DSA_RUBRIC_FILE = Path("output/dsa_rubrics.json")
OOP_RUBRIC_FILE = Path("output/oop_rubrics.json")


def extract_json(text):
    """Extract JSON even if Ollama adds extra text or markdown."""

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


def fix_marks(criteria, total_marks):
    """
    Make sure the criteria marks add up exactly to total_marks.
    This is handled in Python instead of trusting the LLM.
    """

    if not criteria:
        return []

    # Convert marks to integers
    for item in criteria:
        try:
            item["marks"] = max(1, int(item.get("marks", 1)))
        except (ValueError, TypeError):
            item["marks"] = 1

    current_total = sum(item["marks"] for item in criteria)

    # Reduce marks if total is too high
    while current_total > total_marks:
        changed = False

        for item in reversed(criteria):
            if item["marks"] > 1:
                item["marks"] -= 1
                current_total -= 1
                changed = True

                if current_total == total_marks:
                    break

        if not changed:
            break

    # Add marks if total is too low
    index = 0

    while current_total < total_marks:
        criteria[index % len(criteria)]["marks"] += 1
        current_total += 1
        index += 1

    return criteria


def generate_rubric(question_id, question, model_answer, total_marks=10):
    """Generate a rubric using the local Ollama model."""

    prompt = f"""
You are an expert university examiner.

Create a grading rubric for the following question using ONLY the
information present in the model answer.

Question ID:
{question_id}

Question:
{question}

Model Answer:
{model_answer}

Generate between 3 and 7 important evaluation criteria.

Each criterion must represent an important concept, explanation,
definition, type, example, feature, or other meaningful point
contained in the model answer.

Do NOT invent information that is not present in the model answer.

The total examination marks are {total_marks}.

IMPORTANT:
The marks do not need to add up to {total_marks}. The Python program
will adjust the distribution automatically.

Return ONLY valid JSON.

Use exactly this format:

{{
    "criteria": [
        {{
            "criterion": "Definition of the concept",
            "marks": 2
        }},
        {{
            "criterion": "Important concept",
            "marks": 2
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
            format="json"
        )

        content = response["message"]["content"]

    except Exception as error:
        print(f"[ERROR] Ollama failed for {question_id}: {error}")
        return None

    rubric_data = extract_json(content)

    if not rubric_data:
        print(f"[ERROR] Invalid JSON returned for {question_id}")
        return None

    criteria = rubric_data.get("criteria")

    if not isinstance(criteria, list) or not criteria:
        print(f"[ERROR] No valid criteria generated for {question_id}")
        return None

    # Clean criteria
    cleaned_criteria = []

    for item in criteria:

        if not isinstance(item, dict):
            continue

        criterion = str(item.get("criterion", "")).strip()

        if not criterion:
            continue

        try:
            marks = int(item.get("marks", 1))
        except (ValueError, TypeError):
            marks = 1

        cleaned_criteria.append(
            {
                "criterion": criterion,
                "marks": marks
            }
        )

    if not cleaned_criteria:
        print(f"[ERROR] Empty criteria for {question_id}")
        return None

    # Limit to maximum 7 criteria
    cleaned_criteria = cleaned_criteria[:7]

    # Fix total marks in Python
    cleaned_criteria = fix_marks(
        cleaned_criteria,
        total_marks
    )

    final_total = sum(
        item["marks"]
        for item in cleaned_criteria
    )

    rubric = {
        "question_id": question_id,
        "question": question,
        "criteria": cleaned_criteria,
        "total_marks": final_total
    }

    return rubric


def load_model_answers(file_path):
    """Load model answers JSON."""

    if not file_path.exists():
        print(f"[ERROR] Model answer file not found: {file_path}")
        return {}

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception as error:
        print(f"[ERROR] Could not load {file_path}: {error}")
        return {}


def generate_all_rubrics(
    model_answers,
    subject,
    total_marks=10
):
    """Generate and save rubrics for all questions."""

    rubrics = {}

    for question_id, data in model_answers.items():

        print()
        print(f"Generating rubric for {question_id}...")

        if isinstance(data, dict):
            question = data.get("question", "")
            model_answer = data.get("model_answer", "")
        else:
            question = ""
            model_answer = str(data)

        if not model_answer:
            print(
                f"[ERROR] No model answer found for {question_id}"
            )
            continue

        rubric = generate_rubric(
            question_id,
            question,
            model_answer,
            total_marks
        )

        if rubric is None:
            print(
                f"[FAILED] Rubric generation failed for {question_id}"
            )
            continue

        # Final validation
        marks_total = sum(
            item["marks"]
            for item in rubric["criteria"]
        )

        if marks_total != total_marks:
            print(
                f"[FAILED] {question_id}: "
                f"marks total is {marks_total}"
            )
            continue

        rubrics[question_id] = rubric

        # Save to MongoDB
        try:
            save_rubric(
                subject,
                question_id,
                rubric
            )

            print(
                f"[SUCCESS] {subject} {question_id} "
                f"generated and saved to MongoDB "
                f"({marks_total}/{total_marks})"
            )

        except Exception as error:
            print(
                f"[ERROR] MongoDB save failed for "
                f"{subject} {question_id}: {error}"
            )

    return rubrics


def save_rubrics(rubrics, output_file):
    """Save rubrics to JSON."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            rubrics,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"[SUCCESS] Rubrics saved to: {output_file}"
    )


def process_subject(
    subject,
    model_file,
    output_file
):
    """Generate rubrics for one subject."""

    print()
    print("-" * 70)
    print(f"GENERATING {subject} RUBRICS")
    print("-" * 70)

    model_answers = load_model_answers(
        model_file
    )

    if not model_answers:
        print(
            f"[ERROR] No model answers found for {subject}"
        )
        return

    print(
        f"Model questions: {len(model_answers)}"
    )

    rubrics = generate_all_rubrics(
        model_answers,
        subject,
        TOTAL_MARKS
    )

    save_rubrics(
        rubrics,
        output_file
    )

    print(
        f"{subject} rubrics generated: "
        f"{len(rubrics)}/{len(model_answers)}"
    )


def main():

    print()
    print("=" * 70)
    print("AUTOMATIC RUBRIC GENERATION")
    print("=" * 70)

    print()
    print(f"Local LLM : {MODEL_NAME}")
    print(f"Total marks per question : {TOTAL_MARKS}")

    # DSA
    process_subject(
        "DSA",
        DSA_MODEL_FILE,
        DSA_RUBRIC_FILE
    )

    # OOP
    process_subject(
        "OOP",
        OOP_MODEL_FILE,
        OOP_RUBRIC_FILE
    )

    print()
    print("=" * 70)
    print("RUBRIC GENERATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
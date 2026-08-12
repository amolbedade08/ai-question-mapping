import json
from pathlib import Path

from .loader import (
    load_student,
    load_model_answers
)

from .mapper import map_questions


STUDENT_FILE = Path(
    "input/student1.json"
)

MODEL_FILE = Path(
    "model_answers/model_answers.json"
)

OUTPUT_FILE = Path(
    "output/question_mapping_student1.json"
)


def run_mapping():

    # ---------------------------------------------
    # Load student OCR questions
    # ---------------------------------------------

    student = load_student(
        STUDENT_FILE
    )

    # ---------------------------------------------
    # Load model questions and answers
    # ---------------------------------------------

    model_answers = load_model_answers(
        MODEL_FILE
    )

    # ---------------------------------------------
    # Map student questions to model questions
    # ---------------------------------------------

    mappings = map_questions(
        student["answers"],
        model_answers
    )

    # ---------------------------------------------
    # Prepare output
    # ---------------------------------------------

    result = {
        "student": student["student"],
        "mappings": mappings
    }

    # ---------------------------------------------
    # Create output directory
    # ---------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------
    # Save mapping
    # ---------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Question mapping completed: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    run_mapping()   
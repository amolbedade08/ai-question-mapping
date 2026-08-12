import json
from pathlib import Path


def load_json(path):
    """
    Load a JSON file using UTF-8 encoding.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        try:
            return json.load(file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in {path}: {exc}"
            ) from exc


def load_student(path):
    """
    Load student OCR answer JSON.

    Expected structure:

    {
        "student": "student1",
        "answers": {
            "Q1": "...",
            "Q2": "..."
        }
    }
    """

    data = load_json(path)

    if not isinstance(data, dict):
        raise ValueError(
            "Student data must be a JSON object."
        )

    if "student" not in data:
        raise ValueError(
            "Missing 'student' field."
        )

    if "answers" not in data:
        raise ValueError(
            "Missing 'answers' field."
        )

    if not isinstance(data["answers"], dict):
        raise ValueError(
            "'answers' must be an object."
        )

    return data


def load_model_answers(path):
    """
    Load model answers.

    Expected structure:

    {
        "Q1": {
            "question": "...",
            "model_answer": "..."
        },
        "Q2": {
            "question": "...",
            "model_answer": "..."
        }
    }
    """

    data = load_json(path)

    if not isinstance(data, dict):
        raise ValueError(
            "Model answers must be a JSON object."
        )

    return data
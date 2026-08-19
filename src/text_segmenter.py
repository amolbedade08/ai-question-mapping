import re
from pathlib import Path


QUESTION_PATTERN = re.compile(
    r"(?i)(?:^|\s)(?:question\s*)?q?\s*(\d{1,3})\s*[\.\):\-]?"
)


def normalize_question_number(number):
    """Convert a question number into Q1, Q2, Q3 format."""
    return f"Q{int(number)}"


def segment_text(text):
    """
    Split OCR text into question-wise answers.

    Supports formats such as:
        Q1 ...
        Q.1 ...
        Q 1 ...
        Q1) ...
        Question 1 ...

    Returns:
        {
            "Q1": "...",
            "Q2": "..."
        }
    """

    matches = list(QUESTION_PATTERN.finditer(text))

    if not matches:
        return {
            "UNKNOWN": text.strip()
        }

    answers = {}

    for index, match in enumerate(matches):

        question_number = normalize_question_number(
            match.group(1)
        )

        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        answer = text[start:end].strip()

        # Remove leading punctuation/noise
        answer = re.sub(
            r"^[\s\.\:\)\-]+",
            "",
            answer
        ).strip()

        if question_number in answers:
            # Merge duplicate question numbers
            answers[question_number] += " " + answer
        else:
            answers[question_number] = answer

    return answers


def process_student_file(file_path):
    """
    Read one OCR TXT file and convert it to student JSON structure.
    """

    file_path = Path(file_path)

    text = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    answers = segment_text(text)

    return {
        "student": file_path.stem,
        "answers": answers
    }
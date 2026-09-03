import json
import re
from pathlib import Path


TXT_INPUT_DIR = Path("input_txt")
JSON_OUTPUT_DIR = Path("input")


def normalize_question_number(raw_number):
    """
    Convert OCR question numbers into Q1, Q2, Q3, ...
    """

    try:
        return f"Q{int(raw_number)}"

    except (ValueError, TypeError):
        return None


def is_question_marker(line):
    """
    Detect question/answer boundaries commonly produced by OCR.

    Supported examples:

        Q1
        Q 1
        Q.1
        Question 1
        Question No. 1

        ANS 10
        ANS: 10
        ANSWER 10

        Ans ①
        Ans ②
        Ans ③
        Ans ④

        1.
        2.
        3.
        4.

        1)
        2)
        3)
        4)

        1→
        2→
        3→
        4→

        1->
        2->
        3->
        4->
    """

    line = line.strip()

    # =========================================================
    # 1. ANS 10 / ANS: 10 / ANSWER 10
    # =========================================================

    match = re.match(
        r"^\s*ANS(?:WER)?\s*[:.]?\s*(\d+)\b",
        line,
        re.IGNORECASE
    )

    if match:

        number = int(match.group(1))

        # OCR representation of first question.
        #
        # Example from student_6:
        # ANS 10 Inheritance...
        #
        # This represents Q1.
        if number == 10:
            return "Q1"

        if 1 <= number <= 20:
            return normalize_question_number(number)

    # =========================================================
    # 2. OCR CIRCLED NUMBERS
    # =========================================================

    circled_numbers = {
        "①": "Q1",
        "②": "Q2",
        "③": "Q3",
        "④": "Q4",
        "⑤": "Q5",
        "⑥": "Q6",
        "⑦": "Q7",
        "⑧": "Q8",
        "⑨": "Q9",
        "⑩": "Q10",
    }

    for symbol, question_id in circled_numbers.items():

        if re.match(
            rf"^\s*ANS(?:WER)?\s*[:.]?\s*{re.escape(symbol)}",
            line,
            re.IGNORECASE
        ):
            return question_id

    # =========================================================
    # 3. NORMAL Q1 / Q 1 / Q.1 / QUESTION 1
    # =========================================================

    match = re.match(
        r"^\s*(?:Q|Question)\s*(?:No\.)?\s*[\.:]?\s*(\d+)\b",
        line,
        re.IGNORECASE
    )

    if match:

        return normalize_question_number(
            match.group(1)
        )

    # =========================================================
    # 4. PLAIN NUMBERED QUESTIONS
    #
    # Examples:
    #
    # 1. A data structure...
    # 2. An algorithm...
    # 3. Complexity analysis...
    # 4. Array...
    #
    # Also:
    #
    # 1→ A data structure...
    # 2→ An algorithm...
    #
    # Also:
    #
    # 1) A data structure...
    # =========================================================

    match = re.match(
        r"^\s*(\d+)\s*(?:[.)]|→|->|➜|➝|➞)\s+",
        line
    )

    if match:

        number = int(match.group(1))

        if 1 <= number <= 20:

            return normalize_question_number(
                number
            )

    return None


def remove_question_marker(line):
    """
    Remove question marker from the beginning of a line.

    Examples:

        1. A data structure...
        ->
        A data structure...

        1→ A data structure...
        ->
        A data structure...

        Q1 A data structure...
        ->
        A data structure...

        ANS 10 Inheritance...
        ->
        Inheritance...
    """

    line = line.strip()

    # =========================================================
    # Remove Q1 / Q 1 / Q.1 / Question 1
    # =========================================================

    line = re.sub(
        r"^\s*(?:Q|Question)\s*(?:No\.)?\s*[\.:]?\s*\d+\s*",
        "",
        line,
        flags=re.IGNORECASE
    )

    # =========================================================
    # Remove numbered marker
    #
    # 1.
    # 1)
    # 1→
    # 1->
    # =========================================================

    line = re.sub(
        r"^\s*\d+\s*(?:[.)]|→|->|➜|➝|➞)\s*",
        "",
        line
    )

    # =========================================================
    # Remove ANS 10 / ANS: 10 / ANSWER 10
    # =========================================================

    line = re.sub(
        r"^\s*ANS(?:WER)?\s*[:.]?\s*\d+\s*",
        "",
        line,
        flags=re.IGNORECASE
    )

    # =========================================================
    # Remove circled answer markers
    #
    # Ans ①
    # Ans ②
    # Ans ③
    # =========================================================

    line = re.sub(
        r"^\s*ANS(?:WER)?\s*[:.]?\s*[①②③④⑤⑥⑦⑧⑨⑩]\s*",
        "",
        line,
        flags=re.IGNORECASE
    )

    return line.strip()


def clean_answer_text(text):
    """
    Perform basic OCR cleanup without changing
    the actual meaning of the student's answer.
    """

    # ---------------------------------------------------------
    # Remove OCR special token
    # ---------------------------------------------------------

    text = text.replace(
        "<|im_",
        ""
    )

    # ---------------------------------------------------------
    # Replace tabs with spaces
    # ---------------------------------------------------------

    text = text.replace(
        "\t",
        " "
    )

    # ---------------------------------------------------------
    # Normalize multiple spaces
    # ---------------------------------------------------------

    text = re.sub(
        r"[ ]+",
        " ",
        text
    )

    # ---------------------------------------------------------
    # Normalize excessive blank lines
    # ---------------------------------------------------------

    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


def convert_txt_to_json(txt_path, output_dir):
    """
    Convert one OCR TXT file into question-wise JSON.
    """

    # =========================================================
    # Read TXT
    # =========================================================

    text = txt_path.read_text(
        encoding="utf-8",
        errors="replace"
    )

    lines = text.splitlines()

    # =========================================================
    # Storage
    # =========================================================

    answers = {}

    current_question = None
    current_lines = []

    # =========================================================
    # Process every line
    # =========================================================

    for line in lines:

        question_id = is_question_marker(
            line
        )

        # -----------------------------------------------------
        # New question found
        # -----------------------------------------------------

        if question_id:

            # Save previous question first.
            if current_question is not None:

                answer = clean_answer_text(
                    "\n".join(current_lines)
                )

                if answer:

                    answers[current_question] = answer

            # Start new question.
            current_question = question_id

            current_lines = []

            # Remove marker from current line.
            remaining_text = remove_question_marker(
                line
            )

            if remaining_text:

                current_lines.append(
                    remaining_text
                )

        # -----------------------------------------------------
        # Normal answer line
        # -----------------------------------------------------

        else:

            if current_question is not None:

                current_lines.append(
                    line
                )

    # =========================================================
    # Save final question
    # =========================================================

    if current_question is not None:

        answer = clean_answer_text(
            "\n".join(current_lines)
        )

        if answer:

            answers[current_question] = answer

    # =========================================================
    # Create output JSON
    # =========================================================

    output_data = {
        "student": txt_path.stem,
        "answers": answers
    }

    # =========================================================
    # Make output directory
    # =========================================================

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # =========================================================
    # Output filename
    # =========================================================

    output_path = (
        output_dir /
        f"{txt_path.stem}.json"
    )

    # =========================================================
    # Write JSON
    # =========================================================

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"[SUCCESS] "
        f"{txt_path.name} -> "
        f"{output_path.name}"
    )

    return output_path


def convert_all_txt():
    """
    Convert every TXT file from input_txt
    into JSON files inside input.
    """

    # =========================================================
    # Make output directory
    # =========================================================

    JSON_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # =========================================================
    # Find TXT files
    # =========================================================

    txt_files = sorted(
        TXT_INPUT_DIR.glob("*.txt")
    )

    if not txt_files:

        print(
            "No TXT files found."
        )

        return

    # =========================================================
    # Conversion counter
    # =========================================================

    success_count = 0

    # =========================================================
    # Convert each TXT file
    # =========================================================

    for txt_file in txt_files:

        try:

            convert_txt_to_json(
                txt_file,
                JSON_OUTPUT_DIR
            )

            success_count += 1

        except Exception as error:

            print(
                f"[ERROR] Failed to convert "
                f"{txt_file.name}: {error}"
            )

    # =========================================================
    # Final result
    # =========================================================

    print(
        f"\nConversion completed: "
        f"{success_count}/{len(txt_files)} file(s)"
    )


def main():
    """
    Main entry point.
    """

    convert_all_txt()


if __name__ == "__main__":
    main()
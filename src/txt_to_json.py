import json
import re
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

TXT_INPUT_DIR = Path("input_txt")
JSON_OUTPUT_DIR = Path("input")


# ============================================================
# QUESTION NUMBER NORMALIZATION
# ============================================================

def normalize_question_number(raw_number):
    """
    Convert a question number into Q1, Q2, Q3, ...
    """

    try:
        return f"Q{int(raw_number)}"

    except (ValueError, TypeError):
        return None


# ============================================================
# QUESTION MARKER DETECTION
# ============================================================

def is_explicit_question_marker(line):
    """
    Detect strong / explicit question markers.

    These are safe because they are unlikely to be
    normal numbered points inside an answer.

    Supported:

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
    """

    line = line.strip()

    if not line:
        return None

    # ========================================================
    # 1. ANS 10 / ANS:10 / ANSWER 10
    # ========================================================

    match = re.match(
        r"^\s*ANS(?:WER)?\s*[:.]?\s*(\d+)\b",
        line,
        re.IGNORECASE
    )

    if match:
        number = int(match.group(1))

        # OCR commonly converts Q1 to ANS 10
        if number == 10:
            return "Q1"

        if 1 <= number <= 20:
            return normalize_question_number(number)

    # ========================================================
    # 2. CIRCLED NUMBERS
    # ========================================================

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

        pattern = (
            rf"^\s*ANS(?:WER)?\s*[:.]?\s*"
            rf"{re.escape(symbol)}"
        )

        if re.match(
            pattern,
            line,
            re.IGNORECASE
        ):
            return question_id

    # ========================================================
    # 3. Q1 / Q 1 / Q.1 / QUESTION 1
    # ========================================================

    match = re.match(
        r"^\s*(?:Q|Question)\s*(?:No\.)?\s*[\.:]?\s*(\d+)\b",
        line,
        re.IGNORECASE
    )

    if match:
        return normalize_question_number(
            match.group(1)
        )

    return None


# ============================================================
# PLAIN QUESTION MARKER
# ============================================================

def get_plain_question_number(line):
    """
    Detect plain numbered question formats.

    Supported:

        1. Question text
        2. Question text
        3) Question text
        4→ Question text
        (4) Question text

    IMPORTANT:
    This function is only used when the line appears
    at a question boundary. This prevents answer lists
    such as:

        1. Input
        2. Output
        3. Definiteness

    from becoming Q1, Q2, Q3.
    """

    line = line.strip()

    # ========================================================
    # 1. (4) Array
    # ========================================================

    match = re.match(
        r"^\s*\((\d+)\)\s+",
        line
    )

    if match:
        number = int(match.group(1))

        if 1 <= number <= 20:
            return normalize_question_number(number)

    # ========================================================
    # 2. 1. Question
    # 3. 1) Question
    # 4. 1→ Question
    # 5. 1-> Question
    # ========================================================

    match = re.match(
        r"^\s*(\d+)\s*(?:[.)]|→|->|➜|➝|➞)\s+",
        line
    )

    if match:
        number = int(match.group(1))

        if 1 <= number <= 20:
            return normalize_question_number(number)

    return None


# ============================================================
# QUESTION MARKER
# ============================================================

def is_question_marker(
    line,
    expected_question_number=None,
    previous_line_blank=False
):
    """
    Detect whether a line starts a new question.

    Detection strategy:

    1. Strong markers such as Q1, Q2, ANS 10 are
       always accepted.

    2. Plain numbered markers such as 1., 2., (3)
       are accepted ONLY when:
          - they are the expected next question number
          - AND they appear after a blank line

    This prevents numbered answer points from being
    incorrectly treated as new questions.
    """

    line = line.strip()

    if not line:
        return None

    # ========================================================
    # EXPLICIT MARKERS
    # ========================================================

    explicit_question = is_explicit_question_marker(line)

    if explicit_question:
        return explicit_question

    # ========================================================
    # PLAIN NUMBERED QUESTION
    # ========================================================

    if not previous_line_blank:
        return None

    plain_question = get_plain_question_number(line)

    if not plain_question:
        return None

    # ========================================================
    # EXPECTED QUESTION NUMBER CHECK
    # ========================================================

    if expected_question_number is not None:

        expected_id = f"Q{expected_question_number}"

        if plain_question != expected_id:
            return None

    return plain_question


# ============================================================
# REMOVE QUESTION MARKER
# ============================================================

def remove_question_marker(line):
    """
    Remove the question marker from the beginning
    of a question line.

    Examples:

        Q1 A data structure...
        ->
        A data structure...

        Q2) An algorithm...
        ->
        An algorithm...

        4. Array...
        ->
        Array...

        (4) Array...
        ->
        Array...

        ANS 10 Inheritance...
        ->
        Inheritance...

        Ans ② OOP...
        ->
        OOP...
    """

    line = line.strip()

    # ========================================================
    # Q1 / Q 1 / Q.1 / Question 1
    # ========================================================

    line = re.sub(
        r"^\s*(?:Q|Question)\s*(?:No\.)?\s*[\.:]?\s*\d+\s*[\):.]?\s*",
        "",
        line,
        flags=re.IGNORECASE
    )

    # ========================================================
    # ANS 10 / ANS:10 / ANSWER 10
    # ========================================================

    line = re.sub(
        r"^\s*ANS(?:WER)?\s*[:.]?\s*\d+\s*",
        "",
        line,
        flags=re.IGNORECASE
    )

    # ========================================================
    # ANS ① / ANS ② / ...
    # ========================================================

    line = re.sub(
        r"^\s*ANS(?:WER)?\s*[:.]?\s*[①②③④⑤⑥⑦⑧⑨⑩]\s*",
        "",
        line,
        flags=re.IGNORECASE
    )

    # ========================================================
    # (1) / (2) / (3) / (4)
    # ========================================================

    line = re.sub(
        r"^\s*\(\d+\)\s*",
        "",
        line
    )

    # ========================================================
    # 1. / 1) / 1→ / 1-> / etc.
    # ========================================================

    line = re.sub(
        r"^\s*\d+\s*(?:[.)]|→|->|➜|➝|➞)\s*",
        "",
        line
    )

    return line.strip()


# ============================================================
# OCR TEXT CLEANING
# ============================================================

def clean_answer_text(text):
    """
    Perform basic OCR cleanup without changing
    the actual meaning of the student's answer.
    """

    # --------------------------------------------------------
    # Remove OCR special token
    # --------------------------------------------------------

    text = text.replace(
        "<|im_",
        ""
    )

    # --------------------------------------------------------
    # Replace tabs
    # --------------------------------------------------------

    text = text.replace(
        "\t",
        " "
    )

    # --------------------------------------------------------
    # Normalize spaces
    # --------------------------------------------------------

    text = re.sub(
        r"[ ]+",
        " ",
        text
    )

    # --------------------------------------------------------
    # Remove spaces before punctuation
    # --------------------------------------------------------

    text = re.sub(
        r"\s+([,.;:])",
        r"\1",
        text
    )

    # --------------------------------------------------------
    # Normalize excessive blank lines
    # --------------------------------------------------------

    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# CONVERT ONE TXT FILE
# ============================================================

def convert_txt_to_json(
    txt_path,
    output_dir
):
    """
    Convert one OCR TXT file into question-wise JSON.
    """

    # ========================================================
    # READ TXT
    # ========================================================

    text = txt_path.read_text(
        encoding="utf-8",
        errors="replace"
    )

    lines = text.splitlines()

    # ========================================================
    # STORAGE
    # ========================================================

    answers = {}

    current_question = None
    current_lines = []

    # Next question we expect.
    #
    # Example:
    # after Q1 -> expect Q2
    # after Q2 -> expect Q3
    #
    expected_question_number = 1

    previous_line_blank = True

    # ========================================================
    # PROCESS EVERY LINE
    # ========================================================

    for line in lines:

        stripped_line = line.strip()

        # ----------------------------------------------------
        # Determine whether this is a question marker
        # ----------------------------------------------------

        question_id = is_question_marker(
            line,
            expected_question_number=expected_question_number,
            previous_line_blank=previous_line_blank
        )

        # ----------------------------------------------------
        # NEW QUESTION
        # ----------------------------------------------------

        if question_id:

            # Save previous question
            if current_question is not None:

                answer = clean_answer_text(
                    "\n".join(current_lines)
                )

                if answer:
                    answers[current_question] = answer

            # Start new question
            current_question = question_id
            current_lines = []

            # Remove question marker
            remaining_text = remove_question_marker(
                line
            )

            if remaining_text:
                current_lines.append(
                    remaining_text
                )

            # Update expected question number
            try:
                expected_question_number = (
                    int(question_id[1:]) + 1
                )

            except (ValueError, TypeError):
                expected_question_number = None

        # ----------------------------------------------------
        # NORMAL ANSWER LINE
        # ----------------------------------------------------

        else:

            if current_question is not None:
                current_lines.append(line)

        # ----------------------------------------------------
        # Track blank line
        # ----------------------------------------------------

        previous_line_blank = (
            stripped_line == ""
        )

    # ========================================================
    # SAVE FINAL QUESTION
    # ========================================================

    if current_question is not None:

        answer = clean_answer_text(
            "\n".join(current_lines)
        )

        if answer:
            answers[current_question] = answer

    # ========================================================
    # CREATE OUTPUT JSON
    # ========================================================

    output_data = {
        "student": txt_path.stem,
        "answers": answers
    }

    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # OUTPUT FILE
    # ========================================================

    output_path = (
        output_dir /
        f"{txt_path.stem}.json"
    )

    # ========================================================
    # WRITE JSON
    # ========================================================

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

    print(
        f"          Questions detected: "
        f"{len(answers)}"
    )

    return output_path


# ============================================================
# CONVERT ALL TXT FILES
# ============================================================

def convert_all_txt():
    """
    Convert every TXT file from input_txt
    into JSON files inside input.
    """

    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    JSON_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # FIND TXT FILES
    # ========================================================

    txt_files = sorted(
        TXT_INPUT_DIR.glob("*.txt")
    )

    if not txt_files:

        print(
            "No TXT files found in input_txt/"
        )

        return

    # ========================================================
    # CONVERSION COUNTER
    # ========================================================

    success_count = 0

    # ========================================================
    # CONVERT EACH FILE
    # ========================================================

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

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print(
        f"Conversion completed: "
        f"{success_count}/{len(txt_files)} file(s)"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    convert_all_txt()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
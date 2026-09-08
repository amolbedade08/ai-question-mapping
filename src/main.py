import sys
import json
from pathlib import Path

from .loader import load_student, load_model_answers
from .mapper import map_questions
from .subject_detector import detect_subject
from .database import (
    create_tables,
    save_mapping,
    test_connection,
    get_rubric
)
from .txt_to_json import convert_all_txt
from .rubric_generator import generate_rubric


INPUT_DIR = Path("input")

DSA_MODEL_FILE = Path(
    "model_answers/model_answers.json"
)

OOP_MODEL_FILE = Path(
    "model_answers/oop_model_answers.json"
)

OUTPUT_DIR = Path("output")


def get_or_generate_rubric(
    subject,
    question_id,
    model_answers
):
    """Get rubric from MongoDB or generate it if missing."""

    rubric = get_rubric(
        subject,
        question_id
    )

    if rubric:
        print(
            f"[RUBRIC] {subject} {question_id} "
            f"loaded from MongoDB"
        )
        return rubric

    print(
        f"[RUBRIC] {subject} {question_id} "
        f"not found. Generating..."
    )

    model_data = model_answers.get(
        question_id
    )

    if not model_data:
        print(
            f"[WARNING] Model answer not found "
            f"for {question_id}"
        )
        return None

    if isinstance(model_data, dict):
        question = model_data.get(
            "question",
            ""
        )
        model_answer = model_data.get(
            "model_answer",
            ""
        )
    else:
        question = ""
        model_answer = str(model_data)

    if not model_answer:
        print(
            f"[WARNING] Empty model answer "
            f"for {question_id}"
        )
        return None

    rubric = generate_rubric(
        question_id,
        question,
        model_answer,
        total_marks=10
    )

    if rubric:
        print(
            f"[SUCCESS] Rubric generated for "
            f"{subject} {question_id}"
        )

    return rubric


def process_student(
    student_file,
    dsa_model_answers,
    oop_model_answers
):
    """Process one student's JSON file."""

    try:

        student = load_student(
            student_file
        )

        student_id = student["student"]

        print()
        print("=" * 60)
        print(
            f"Processing: {student_id}"
        )
        print("=" * 60)

        # --------------------------------------------------
        # Subject Detection
        # --------------------------------------------------

        subject_result = detect_subject(
            student["answers"],
            dsa_model_answers,
            oop_model_answers
        )

        subject = subject_result["subject"]

        if subject == "UNKNOWN":

            print(
                f"[WARNING] Could not confidently "
                f"identify subject for {student_id}."
            )

            return False

        # --------------------------------------------------
        # Select Model
        # --------------------------------------------------

        if subject == "DSA":

            model_answers = dsa_model_answers
            model_file = DSA_MODEL_FILE

        else:

            model_answers = oop_model_answers
            model_file = OOP_MODEL_FILE

        print()
        print(
            f"[SUBJECT] {subject}"
        )
        print(
            f"[MODEL] {model_file}"
        )

        # --------------------------------------------------
        # Question Mapping
        # --------------------------------------------------

        print()
        print("-" * 60)
        print("QUESTION MAPPING")
        print("-" * 60)

        mappings = map_questions(
            student["answers"],
            model_answers
        )

        # --------------------------------------------------
        # Save Mapping to MongoDB
        # --------------------------------------------------

        for question_id, mapping in mappings.items():

            save_mapping(
                student_id,
                question_id,
                mapping
            )

        print(
            "[DATABASE] Question mappings saved"
        )

        # --------------------------------------------------
        # Rubric Generation / Retrieval
        # --------------------------------------------------

        print()
        print("-" * 60)
        print("RUBRIC GENERATION / RETRIEVAL")
        print("-" * 60)

        rubrics = {}

        for student_question, mapping in mappings.items():

            if mapping.get("status") != "matched":
                continue

            model_question = mapping.get(
                "matched_model_question"
            )

            if not model_question:
                continue

            rubric = get_or_generate_rubric(
                subject,
                model_question,
                model_answers
            )

            if rubric:
                rubrics[student_question] = rubric

        # --------------------------------------------------
        # Save Output
        # --------------------------------------------------

        result = {
            "student": student_id,
            "subject": subject,
            "subject_detection": subject_result,
            "model_file": str(model_file),
            "mappings": mappings,
            "rubrics": rubrics
        }

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = (
            OUTPUT_DIR /
            f"question_mapping_{student_id}.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        print()
        print(
            f"[SUCCESS] Processing completed: "
            f"{student_id}"
        )

        print(
            f"[OUTPUT] {output_file}"
        )

        print(
            "[DATABASE] Saved to MongoDB"
        )

        print(
            f"[RUBRIC] Rubrics available: "
            f"{len(rubrics)}"
        )

        return True

    except Exception as error:

        print()
        print(
            f"[ERROR] {student_file.name}: "
            f"{error}"
        )

        return False


def find_student_file(student_id):
    """Find a specific student JSON file."""

    # Allow:
    # student_1
    # student_1.json

    student_id = Path(student_id).stem

    student_file = (
        INPUT_DIR /
        f"{student_id}.json"
    )

    return student_file


def main():

    print(
        "=" * 60
    )

    print(
        "AI QUESTION MAPPING PIPELINE"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------
    # STEP 0: MongoDB
    # --------------------------------------------------

    print()
    print(
        "Checking MongoDB..."
    )

    if not test_connection():

        print()
        print(
            "MongoDB connection failed."
        )

        print(
            "Please make sure MongoDB is running."
        )

        return

    print(
        "MongoDB is connected."
    )

    try:

        create_tables()

    except Exception as error:

        print(
            f"[ERROR] MongoDB setup failed: "
            f"{error}"
        )

        return

    # --------------------------------------------------
    # STEP 1: TXT → JSON
    # --------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "STEP 1: TXT → JSON"
    )

    print(
        "=" * 60
    )

    try:

        convert_all_txt()

    except Exception as error:

        print(
            f"[ERROR] TXT conversion failed: "
            f"{error}"
        )

        return

    # --------------------------------------------------
    # STEP 2: Load Model Answers
    # --------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "STEP 2: LOAD MODEL ANSWERS"
    )

    print(
        "=" * 60
    )

    if not DSA_MODEL_FILE.exists():

        print(
            "[ERROR] DSA model answer file not found:"
        )

        print(
            DSA_MODEL_FILE
        )

        return

    if not OOP_MODEL_FILE.exists():

        print(
            "[ERROR] OOP model answer file not found:"
        )

        print(
            OOP_MODEL_FILE
        )

        return

    try:

        dsa_model_answers = load_model_answers(
            DSA_MODEL_FILE
        )

        oop_model_answers = load_model_answers(
            OOP_MODEL_FILE
        )

    except Exception as error:

        print(
            f"[ERROR] Could not load model answers: "
            f"{error}"
        )

        return

    print(
        f"[SUCCESS] DSA model loaded from "
        f"{DSA_MODEL_FILE}"
    )

    print(
        f"[SUCCESS] OOP model loaded from "
        f"{OOP_MODEL_FILE}"
    )

    # --------------------------------------------------
    # STEP 3: Decide Which Students to Process
    # --------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "STEP 3: FIND STUDENTS"
    )

    print(
        "=" * 60
    )

    if len(sys.argv) > 1:

        # ----------------------------------------------
        # Specific student requested
        # ----------------------------------------------

        requested_student = sys.argv[1]

        student_file = find_student_file(
            requested_student
        )

        if not student_file.exists():

            print()
            print(
                f"[ERROR] Student file not found:"
            )

            print(
                f"        {student_file}"
            )

            print()
            print(
                "Available students:"
            )

            available_students = sorted(
                INPUT_DIR.glob("student_*.json")
            )

            for file in available_students:

                print(
                    f"        {file.stem}"
                )

            return

        student_files = [
            student_file
        ]

        print(
            f"Selected student: "
            f"{student_file.stem}"
        )

    else:

        # ----------------------------------------------
        # No student specified → process all
        # ----------------------------------------------

        student_files = sorted(
            INPUT_DIR.glob("student_*.json")
        )

        if not student_files:

            print(
                "No student JSON files found."
            )

            return

        print(
            f"Found {len(student_files)} "
            f"student JSON file(s)."
        )

    # --------------------------------------------------
    # STEP 4: Process Students
    # --------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "STEP 4: SUBJECT DETECTION + "
        "QUESTION MAPPING + RUBRIC"
    )

    print(
        "=" * 60
    )

    success_count = 0
    failed_count = 0

    for student_file in student_files:

        success = process_student(
            student_file,
            dsa_model_answers,
            oop_model_answers
        )

        if success:

            success_count += 1

        else:

            failed_count += 1

    # --------------------------------------------------
    # STEP 5: Summary
    # --------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "PIPELINE COMPLETED"
    )

    print(
        "=" * 60
    )

    print(
        f"Successful students : "
        f"{success_count}"
    )

    print(
        f"Failed students     : "
        f"{failed_count}"
    )

    print()

    print(
        f"Output folder : "
        f"{OUTPUT_DIR}"
    )

    print(
        "MongoDB       : "
        "answer_evaluation"
    )

    print(
        "Mapping collection : "
        "question_mappings"
    )

    print(
        "Rubric collection  : "
        "rubrics"
    )


if __name__ == "__main__":
    main()
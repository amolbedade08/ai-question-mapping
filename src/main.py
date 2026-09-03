import json
from pathlib import Path

from .loader import load_student, load_model_answers
from .mapper import map_questions
from .subject_detector import detect_subject
from .database import create_tables, save_mapping, test_connection
from .txt_to_json import convert_all_txt


INPUT_DIR = Path("input")

DSA_MODEL_FILE = Path(
    "model_answers/model_answers.json"
)

OOP_MODEL_FILE = Path(
    "model_answers/oop_model_answers.json"
)

OUTPUT_DIR = Path("output")


def process_student(
    student_file,
    dsa_model_answers,
    oop_model_answers
):
    """Process one student's JSON file."""

    try:

        student = load_student(student_file)

        student_id = student["student"]

        print()
        print("=" * 60)
        print(f"Processing: {student_id}")
        print("=" * 60)

        # --------------------------------------------------
        # Subject detection
        # --------------------------------------------------

        subject_result = detect_subject(
            student["answers"],
            dsa_model_answers,
            oop_model_answers
        )

        subject = subject_result["subject"]

        if subject == "UNKNOWN":

            print()
            print(
                f"[WARNING] Could not confidently identify "
                f"subject for {student_id}."
            )

            return False

        # --------------------------------------------------
        # Select correct model answers
        # --------------------------------------------------

        if subject == "DSA":

            model_answers = dsa_model_answers
            model_file = DSA_MODEL_FILE

        else:

            model_answers = oop_model_answers
            model_file = OOP_MODEL_FILE

        print()
        print(f"[SUBJECT] {subject}")
        print(f"[MODEL] {model_file}")

        # --------------------------------------------------
        # Question mapping
        # --------------------------------------------------

        mappings = map_questions(
            student["answers"],
            model_answers
        )

        # --------------------------------------------------
        # Save output
        # --------------------------------------------------

        result = {
            "student": student_id,
            "subject": subject,
            "subject_detection": subject_result,
            "model_file": str(model_file),
            "mappings": mappings
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
        # Save to MongoDB
        # --------------------------------------------------

        for question_id, mapping in mappings.items():

            save_mapping(
                student_id,
                question_id,
                mapping
            )

        print(
            f"[SUCCESS] Mapping completed: "
            f"{student_id}"
        )

        print(
            f"[OUTPUT] {output_file}"
        )

        print(
            "[DATABASE] Saved to MongoDB"
        )

        return True

    except Exception as error:

        print(
            f"[ERROR] {student_file.name}: "
            f"{error}"
        )

        return False


def main():

    print("=" * 60)
    print("AI QUESTION MAPPING PIPELINE")
    print("=" * 60)

    # --------------------------------------------------
    # 1. MongoDB
    # --------------------------------------------------

    print()
    print("Checking MongoDB...")

    if not test_connection():

        print()
        print("MongoDB connection failed.")
        print("Please make sure MongoDB is running.")

        return

    print("MongoDB is connected.")

    create_tables()

    # --------------------------------------------------
    # 2. TXT → JSON
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("STEP 1: TXT → JSON")
    print("=" * 60)

    try:

        convert_all_txt()

    except Exception as error:

        print(
            f"[ERROR] TXT conversion failed: "
            f"{error}"
        )

        return

    # --------------------------------------------------
    # 3. Load DSA model
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("STEP 2: LOAD MODEL ANSWERS")
    print("=" * 60)

    if not DSA_MODEL_FILE.exists():

        print(
            f"[ERROR] DSA model answer file not found:"
        )

        print(DSA_MODEL_FILE)

        return

    if not OOP_MODEL_FILE.exists():

        print(
            f"[ERROR] OOP model answer file not found:"
        )

        print(OOP_MODEL_FILE)

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
    # 4. Find students
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("STEP 3: FIND STUDENTS")
    print("=" * 60)

    student_files = sorted(
        INPUT_DIR.glob("*.json")
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
    # 5. Process students
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("STEP 4: SUBJECT DETECTION + QUESTION MAPPING")
    print("=" * 60)

    success_count = 0
    failed_count = 0

    for student_file in student_files:

        # Ignore model files accidentally placed in input
        if student_file.name.startswith("model"):
            continue

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
    # 6. Summary
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)

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
        "Collection    : "
        "question_mappings"
    )


if __name__ == "__main__":
    main()
    
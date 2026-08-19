import json
from pathlib import Path

from .text_segmenter import process_student_file


INPUT_DIR = Path("input_txt")
OUTPUT_DIR = Path("segmented_students")


def segment_all_students():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    student_files = sorted(
        INPUT_DIR.glob("*.txt")
    )

    if not student_files:
        print("No TXT files found in input_txt/")
        return

    for student_file in student_files:

        student_data = process_student_file(
            student_file
        )

        output_file = (
            OUTPUT_DIR
            / f"{student_file.stem}.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                student_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"{student_file.name} -> "
            f"{output_file}"
        )

    print(
        f"\nProcessed {len(student_files)} student files."
    )


if __name__ == "__main__":
    segment_all_students()
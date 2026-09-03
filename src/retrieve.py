import sys

from .database import (
    get_student_mappings,
    test_connection
)


def retrieve_student(student_id):
    """Retrieve and display mappings for one student."""

    mappings = get_student_mappings(student_id)

    print()
    print(f"Mappings for {student_id}:")
    print()

    if not mappings:
        print("No mappings found for this student.")
        return

    for mapping in mappings:

        print(
            f"{mapping['student_question']} -> "
            f"{mapping['matched_model_question']} | "
            f"similarity="
            f"{mapping['similarity']:.4f} | "
            f"status="
            f"{mapping['status']}"
        )


def main():

    if not test_connection():

        print(
            "Please start MongoDB or configure "
            "your MongoDB Atlas connection."
        )

        return

    if len(sys.argv) < 2:

        print(
            "Usage: "
            "python -m src.retrieve <student_id>"
        )

        return

    student_id = sys.argv[1]

    retrieve_student(student_id)


if __name__ == "__main__":
    main()
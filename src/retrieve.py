from .database import get_student_mappings


def retrieve_student(student_id):
    mappings = get_student_mappings(student_id)

    if not mappings:
        print(
            f"No mappings found for student: {student_id}"
        )
        return

    print(
        f"\nMappings for {student_id}:"
    )

    for mapping in mappings:

        print(
            f"{mapping['student_question']} "
            f"-> "
            f"{mapping['matched_model_question']} "
            f"| similarity="
            f"{mapping['similarity']:.4f} "
            f"| status="
            f"{mapping['status']}"
        )


if __name__ == "__main__":
    retrieve_student("student1")
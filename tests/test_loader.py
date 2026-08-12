from src.loader import (
    load_student,
    load_model_answers
)


def test_student_loader():

    data = load_student(
        "input/student1.json"
    )

    assert "student" in data
    assert "answers" in data
    assert isinstance(
        data["answers"],
        dict
    )
    assert len(data["answers"]) > 0


def test_model_loader():

    data = load_model_answers(
        "model_answers/model_answers.json"
    )

    assert isinstance(
        data,
        dict
    )

    assert len(data) > 0
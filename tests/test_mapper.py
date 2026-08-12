from src.mapper import map_questions


def test_question_content_mismatch():

    student_answers = {
        "Q1": (
            "Python is a programming language "
            "used for software development."
        )
    }

    model_answers = {
        "Q1": {
            "question": (
                "Explain inheritance and its types."
            ),
            "model_answer": (
                "Inheritance is the OOP mechanism "
                "by which a derived class acquires "
                "the properties and behaviours of "
                "a base class."
            )
        }
    }

    result = map_questions(
        student_answers,
        model_answers
    )

    assert "Q1" in result

    assert (
        result["Q1"]["status"]
        == "unmatched"
    )

    assert (
        result["Q1"][
            "matched_model_question"
        ]
        is None
    )


def test_question_correct_match():

    student_answers = {
        "Q1": (
            "A child class can inherit properties "
            "and methods from a parent class. "
            "This is called inheritance."
        )
    }

    model_answers = {
        "Q1": {
            "question": (
                "Explain inheritance and its types."
            ),
            "model_answer": (
                "Inheritance is the OOP mechanism "
                "by which a derived class acquires "
                "the properties and behaviours of "
                "a base class."
            )
        }
    }

    result = map_questions(
        student_answers,
        model_answers
    )

    assert (
        result["Q1"][
            "matched_model_question"
        ]
        == "Q1"
    )

    assert (
    result["Q1"]["similarity"]
    >= 0.60
)

    assert (
        result["Q1"]["status"]
        == "matched"
    )
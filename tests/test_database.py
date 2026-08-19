from src.database import (
    create_tables,
    save_mapping,
    get_mappings
)


def test_database_storage_and_retrieval():

    create_tables()

    mapping = {
        "matched_model_question": "Q1",
        "similarity": 0.8943,
        "number_match": True,
        "threshold_used": 0.60,
        "status": "matched"
    }

    save_mapping(
        "test_student",
        "Q1",
        mapping
    )

    results = get_mappings(
        "test_student"
    )

    assert len(results) >= 1

    row = results[-1]

    assert row[0] == "Q1"
    assert row[1] == "Q1"
    assert row[2] == 0.8943
    assert row[3] == 1
    assert row[5] == "matched"
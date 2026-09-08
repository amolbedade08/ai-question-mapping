from pymongo import MongoClient
from datetime import datetime


MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "answer_evaluation"

COLLECTION_NAME = "question_mappings"
RUBRIC_COLLECTION_NAME = "rubrics"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

db = client[DATABASE_NAME]

collection = db[COLLECTION_NAME]
rubric_collection = db[RUBRIC_COLLECTION_NAME]


def create_tables():
    """Create unique index for student/question mappings."""

    collection.create_index(
        [("student_id", 1), ("student_question", 1)],
        unique=True
    )


def save_mapping(student_id, question_id, mapping):
    """Save or update one question mapping."""

    document = {
        "student_id": student_id,
        "student_question": question_id,
        "matched_model_question": mapping.get(
            "matched_model_question"
        ),
        "similarity": mapping.get("similarity", 0.0),
        "number_match": mapping.get("number_match", False),
        "threshold_used": mapping.get("threshold_used", 0.0),
        "status": mapping.get("status"),
        "updated_at": datetime.utcnow()
    }

    collection.update_one(
        {
            "student_id": student_id,
            "student_question": question_id
        },
        {
            "$set": document
        },
        upsert=True
    )


def get_mappings(student_id):
    """Retrieve mappings for a student."""

    documents = collection.find(
        {"student_id": student_id},
        {"_id": 0}
    ).sort("student_question", 1)

    rows = []

    for document in documents:
        rows.append((
            document.get("student_question"),
            document.get("matched_model_question"),
            document.get("similarity"),
            document.get("number_match"),
            document.get("threshold_used"),
            document.get("status"),
            document.get("updated_at")
        ))

    return rows


def get_student_mappings(student_id):
    """Retrieve mappings as dictionaries."""

    documents = collection.find(
        {"student_id": student_id},
        {"_id": 0}
    ).sort("student_question", 1)

    mappings = []

    for document in documents:
        mappings.append({
            "student_question":
                document.get("student_question"),

            "matched_model_question":
                document.get("matched_model_question"),

            "similarity":
                document.get("similarity"),

            "number_match":
                bool(document.get("number_match")),

            "threshold":
                document.get("threshold_used"),

            "status":
                document.get("status"),

            "updated_at":
                document.get("updated_at")
        })

    return mappings


def delete_student_mappings(student_id):
    """Delete all mappings for one student."""

    result = collection.delete_many(
        {"student_id": student_id}
    )

    return result.deleted_count


def test_connection():
    """Test local MongoDB connection."""

    try:
        client.admin.command("ping")

        print("MongoDB connection successful!")

        return True

    except Exception as error:

        print("MongoDB connection failed!")
        print(error)

        return False

def save_rubric(subject, question_id, rubric):
    document = {
        "subject": subject,
        "question_id": question_id,
        "question": rubric.get("question", ""),
        "criteria": rubric.get("criteria", []),
        "total_marks": rubric.get("total_marks", 0)
    }

    rubric_collection.update_one(
        {
            "subject": subject,
            "question_id": question_id
        },
        {"$set": document},
        upsert=True
    )

def get_rubric(subject, question_id):
    """Retrieve one rubric from MongoDB."""

    document = rubric_collection.find_one(
        {
            "subject": subject,
            "question_id": question_id
        },
        {"_id": 0}
    )

    return document

def get_subject_rubrics(subject):
    """Retrieve all rubrics for a subject."""

    documents = rubric_collection.find(
        {"subject": subject},
        {"_id": 0}
    ).sort("question_id", 1)

    return list(documents)
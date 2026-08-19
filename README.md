# AI Question Mapping Project

## Overview

This project maps OCR-extracted student answers to the corresponding questions in a model answer document using semantic similarity.

The system is focused specifically on the **question-mapping stage** of an answer-processing pipeline. It does not currently perform answer grading, marks calculation, rubric evaluation, or AI-based feedback generation.

The system supports:

- OCR-extracted student answers
- Question-wise student JSON files
- Model answer JSON files
- DSA and OOP model-answer sets
- Semantic question mapping
- Multiple students
- SQLite database storage
- Student-wise mapping retrieval
- Automated testing

---

## Purpose

OCR extraction can introduce:

- Incorrect question numbers
- OCR noise
- Different question-number formats
- Questions appearing in a different order
- Differences between student and model-answer wording

Therefore, the system does not depend only on question numbers.

Instead, it uses **semantic similarity** to compare student answer content with model-question information and identifies the most relevant model question.

For example:

Student answer:

```text
A child class can inherit properties and methods from a parent class.
```

Model answer:

```text
Inheritance is the OOP mechanism by which a derived class
acquires the properties and behaviours of a base class.
```

Although the wording is different, the system can identify both as referring to the same question.

---

# Project Architecture

```text
Student OCR Text
       |
       v
Question Segmentation
       |
       v
Student JSON
       |
       v
Model Answer Selection
       |
       v
Text Preprocessing
       |
       v
Sentence Embeddings
       |
       v
Semantic Similarity
       |
       v
Question Mapping
       |
       v
SQLite Database
       |
       v
Student-wise Retrieval
```

---

# Project Structure

```text
answer-evaluation/
│
├── input/
│   ├── student1.json
│   ├── student_8.json
│   ├── student_9.json
│   ├── student_10.json
│   ├── student_11.json
│   ├── student_12.json
│   ├── student_13.json
│   └── student_14.json
│
├── model_answers/
│   ├── model_answers.json
│   └── dsa_model_answers.json
│
├── output/
│   ├── question_mapping_student1.json
│   └── mapping.db
│
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── embeddings.py
│   ├── loader.py
│   ├── main.py
│   ├── mapper.py
│   ├── preprocess.py
│   ├── retrieve.py
│   ├── segment_students.py
│   ├── semantic_mapper.py
│   ├── similarity.py
│   └── text_segmenter.py
│
├── tests/
│   ├── test_database.py
│   ├── test_database_retrieval.py
│   ├── test_loader.py
│   ├── test_mapper.py
│   ├── test_preprocess.py
│   ├── test_semantic_mapper.py
│   └── test_similarity.py
│
├── requirements.txt
└── README.md
```

---

# Installation

Create a virtual environment:

```bash
python -m venv .venv
```

## Windows

```powershell
.venv\Scripts\activate
```

## Linux/macOS

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

# Requirements

The project uses Python libraries including:

```text
sentence-transformers
scikit-learn
pytest
```

Sentence Transformers is used for generating semantic embeddings.

Cosine similarity is used to compare the generated embeddings.

---

# Student Input Format

Student answers are stored in JSON format.

Example:

```json
{
    "student": "student1",
    "answers": {
        "Q1": "In Object Oriented Programming inheritance allows a class to acquire properties and behaviours from another class.",
        "Q2": "Object Oriented Programming is a programming paradigm based on objects that contain data and behaviour.",
        "Q3": "Polymorphism allows a single entity to take multiple forms.",
        "Q4": "A class is a blueprint that defines data and behaviour for objects."
    }
}
```

The `student` field identifies the student.

The `answers` object contains the question-wise student answers.

---

# Model Answer Format

The model-answer file contains the question and its reference answer.

Example:

```json
{
    "Q1": {
        "question": "Explain inheritance and its types.",
        "model_answer": "Inheritance is the OOP mechanism by which a derived class acquires the properties and behaviours of a base class."
    },
    "Q2": {
        "question": "Explain Object Oriented Programming and its characteristics.",
        "model_answer": "Object Oriented Programming is a programming paradigm based on objects that bundle data and behaviour."
    },
    "Q3": {
        "question": "Explain polymorphism and its types.",
        "model_answer": "Polymorphism means many forms and allows a function, method or operator to behave differently."
    },
    "Q4": {
        "question": "Explain classes and objects.",
        "model_answer": "A class is a user-defined blueprint or template defining properties and behaviours common to its objects."
    }
}
```

---

# Subject-specific Model Answers

The project currently supports separate model-answer files for different subjects.

```text
model_answers/
│
├── model_answers.json
└── dsa_model_answers.json
```

For example:

```text
OOP Student
    |
    v
model_answers.json
```

and:

```text
DSA Student
    |
    v
dsa_model_answers.json
```

This allows students from different subjects to be mapped against the appropriate model questions.

---

# Question Mapping Process

The mapping process works as follows:

```text
Student Answers
      |
      v
Text Preprocessing
      |
      v
Semantic Embedding
      |
      v
Compare Against Model Questions
      |
      v
Cosine Similarity
      |
      v
Best Candidate
      |
      v
Matched / Unmatched
```

Each student answer is compared against the available model questions.

The candidate with the highest semantic similarity is selected.

---

# Semantic Mapping

The system generates embeddings for the student answer and model-question information using a Sentence Transformer model.

The embeddings are then compared using cosine similarity.

For example:

```text
Student Q1 -> Model Q1
similarity = 0.8943
status = matched
```

The system does not require the student answer and model answer to use exactly the same words.

Semantic similarity allows different wording to still be mapped to the same question.

---

# Question Number Handling

Question numbers are used as **supporting information**, but they are not the only mapping decision.

The system can normalize question identifiers such as:

```text
Q1
Q 1
Q.1
Question 1
1
```

into:

```text
Q1
```

This helps handle variations introduced by OCR.

The system also compares the semantic content of answers against the available model questions.

---

# Similarity Threshold

The mapping uses similarity thresholds to determine whether a mapping is sufficiently strong.

Current development thresholds include:

```text
Same question number:
similarity >= 0.60

Different or uncertain question number:
similarity >= 0.70
```

These are development values and should be evaluated using a larger labelled dataset before being considered production thresholds.

---

# Mapping Status

The system can produce statuses such as:

### `matched`

The best candidate meets the configured similarity threshold.

### `unmatched`

No model question has sufficient similarity to confidently map the student answer.

### `empty_answer`

The student answer is empty.

---

# OCR Handling

OCR extraction may produce incorrect or unusual question numbers.

For example:

```text
Actual:
Q1

OCR:
Q1991
```

The system does not rely exclusively on the question number.

Instead, it compares the semantic content against the available model questions.

This allows a potentially incorrect OCR question identifier to still be mapped based on answer content when sufficient semantic similarity exists.

---

# Example Mapping Output

The generated mapping JSON contains information such as:

```json
{
    "student": "student1",
    "mappings": {
        "Q1": {
            "matched_model_question": "Q1",
            "best_candidate": "Q1",
            "similarity": 0.8943,
            "number_match": true,
            "threshold_used": 0.6,
            "status": "matched"
        }
    }
}
```

The mapping contains:

- Student question
- Matched model question
- Best candidate
- Similarity score
- Question-number match information
- Threshold used
- Mapping status

---

# Multiple Student Support

The system supports processing multiple student JSON files.

For example:

```text
input/
├── student_8.json
├── student_9.json
├── student_10.json
├── student_11.json
├── student_12.json
├── student_13.json
└── student_14.json
```

Each student's mappings are associated with their student ID.

Conceptually:

```text
student_8
    Q1 -> Q1
    Q2 -> Q2
    Q3 -> Q3
    Q4 -> Q4

student_9
    Q1 -> Q1
    Q2 -> Q2
    Q3 -> Q3
    Q4 -> Q4
```

---

# Text Segmentation

The project also contains a text-segmentation component for converting OCR text into question-wise student JSON.

Supported question formats include variations such as:

```text
Q1
Q.1
Q 1
Q1)
Question 1
```

The segmentation process converts the OCR text into:

```json
{
    "student": "student_1",
    "answers": {
        "Q1": "Answer text...",
        "Q2": "Answer text...",
        "Q3": "Answer text...",
        "Q4": "Answer text..."
    }
}
```

This segmented JSON can then be passed to the question-mapping stage.

---

# Database Storage

Mapping results are stored persistently using SQLite.

Database location:

```text
output/mapping.db
```

The database allows mappings to be stored and retrieved without rerunning the semantic mapping process.

Example:

```text
student1
    |
    ├── Q1 -> Q1
    ├── Q2 -> Q2
    ├── Q3 -> Q3
    └── Q4 -> Q4
```

---

# Database Retrieval

Student mappings can be retrieved from the SQLite database.

Example:

```bash
python -m src.retrieve student1
```

Example output:

```text
Mappings for student1:

Q1 -> Q1 | similarity=0.8943 | status=matched
Q2 -> Q2 | similarity=0.8477 | status=matched
Q3 -> Q3 | similarity=0.8788 | status=matched
Q4 -> Q4 | similarity=0.8582 | status=matched
```

The retrieval functionality allows mappings to be accessed using the student ID.

---

# Running the Project

Place the student JSON files inside:

```text
input/
```

Place the appropriate model-answer files inside:

```text
model_answers/
```

Then run:

```bash
python -m src.main
```

The system will process the student answers, perform semantic question mapping, and save the mapping results.

The mappings are also stored in:

```text
output/mapping.db
```

---

# Retrieving a Student's Mapping

To retrieve a student's stored mappings:

```bash
python -m src.retrieve student1
```

Replace `student1` with the required student ID.

For example:

```bash
python -m src.retrieve student_14
```

---

# Testing

Run the complete test suite using:

```bash
pytest -v
```

The current test suite covers:

- Database storage
- Database retrieval
- Student JSON loading
- Model answer loading
- Question mapping
- Incorrect question mapping
- Text preprocessing
- Semantic mapping
- Semantic similarity

Current test result:

```text
10 passed
```

Example:

```text
tests/test_database.py::test_database_storage_and_retrieval PASSED
tests/test_database_retrieval.py::test_retrieve_student_mappings PASSED
tests/test_loader.py::test_student_loader PASSED
tests/test_loader.py::test_model_loader PASSED
tests/test_mapper.py::test_question_content_mismatch PASSED
tests/test_mapper.py::test_question_correct_match PASSED
tests/test_preprocess.py::test_normalize_text PASSED
tests/test_preprocess.py::test_remove_ocr_noise PASSED
tests/test_semantic_mapper.py::test_map_chunks PASSED
tests/test_similarity.py::test_semantic_similarity PASSED

10 passed
```

---

# Example Result

For the OOP sample paper, the system produced:

```text
Student Q1 -> Model Q1 | similarity=0.8943 | status=matched

Student Q2 -> Model Q2 | similarity=0.8477 | status=matched

Student Q3 -> Model Q3 | similarity=0.8788 | status=matched

Student Q4 -> Model Q4 | similarity=0.8582 | status=matched
```

These scores demonstrate the semantic mapping behaviour on the current sample data.

They should not be interpreted as overall mapping accuracy. A proper accuracy measurement requires a larger labelled dataset containing known correct and incorrect mappings.

---

# Current Scope

The current project focuses on the following stages:

1. Student answer loading
2. OCR text preprocessing
3. Question-wise segmentation
4. Semantic embedding generation
5. Question-to-question semantic mapping
6. Similarity calculation
7. Mapping status determination
8. SQLite database storage
9. Student-wise mapping retrieval

The project currently does **not** perform:

- Answer grading
- Marks calculation
- Rubric evaluation
- Answer-quality scoring
- AI-based feedback generation

---

# Future Scope

The broader planned pipeline can be extended as follows:

```text
OCR Extraction
      |
      v
Answer Segmentation
      |
      v
Question Mapping
      |
      v
Answer Comparison
      |
      v
Rubric Evaluation
      |
      v
Marks Calculation
      |
      v
Feedback Generation
```

Possible future improvements include:

- Improved OCR handling
- More robust question segmentation
- Automatic subject detection
- Larger DSA and OOP datasets
- Mapping accuracy evaluation
- Better threshold calibration
- Answer comparison after question mapping
- Rubric-based evaluation
- Marks calculation
- Feedback generation
- Web/API interface
- User authentication
- Student dashboard
- Scalable database integration

---

# Team

- Chaitanya Kulkarni
- Shashank Gangade
- Amol Bedade

---

# Project Status

The current implementation successfully supports:

```text
Semantic Question Mapping
        +
Multiple Student Data
        +
DSA / OOP Model Answers
        +
SQLite Storage
        +
Student-wise Retrieval
        +
Automated Testing
```

The current focus remains on **reliable question mapping**, which will serve as the foundation for the future answer-evaluation stages.
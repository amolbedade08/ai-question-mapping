# AI Question Mapping Project

## Overview

This project is an automated answer-processing pipeline that converts OCR-extracted student answers into question-wise JSON, detects the subject, maps student questions to the corresponding model questions using semantic similarity, generates evaluation rubrics using a local Llama 3.2 model, and evaluates student answers against those rubrics.

The project currently supports:

- OCR-extracted student answers
- TXT-to-question-wise JSON conversion
- DSA and OOP model-answer sets
- Automatic subject detection between DSA and OOP
- Semantic question mapping using Sentence Transformers
- Question-number normalization and supporting number matching
- Similarity thresholds for matched/unmatched decisions
- Multiple-student processing
- Local MongoDB storage
- Student-wise mapping retrieval
- Automatic rubric generation from model answers
- Local Llama 3.2 through Ollama
- MongoDB rubric storage
- Rubric-based student answer evaluation
- Criterion-wise marks calculation
- Total marks calculation
- MongoDB evaluation storage
- Student-wise evaluation JSON output
- Automated testing

---

# Purpose

OCR extraction can introduce:

- Incorrect question numbers
- OCR noise
- Different question-number formats
- Questions appearing in a different order
- Differences between student and model-answer wording

Therefore, the system does not depend only on question numbers.

Instead, it uses semantic similarity to compare student answer content with model-question information and identify the most relevant model question.

For example, a student may write:

```text
A child class can inherit properties and methods from a parent class.
```

while the model answer may describe:

```text
Inheritance is the OOP mechanism by which a derived class
acquires the properties and behaviours of a base class.
```

Although the wording is different, semantic embeddings can identify that both refer to inheritance.

---

# Project Architecture

```text
Student OCR Text
        |
        v
TXT-to-JSON Conversion
        |
        v
Question-wise Student JSON
        |
        v
Subject Detection
        |
        +-------------------+
        |                   |
        v                   v
       DSA                 OOP
        |                   |
        +---------+---------+
                  |
                  v
        Model Answer Selection
                  |
                  v
        Semantic Question Mapping
                  |
                  v
          Matched / Unmatched
                  |
          +-------+--------+
          |                |
          v                v
   MongoDB Mapping     Model Answer
                           |
                           v
                    Local Llama 3.2
                           |
                           v
                    Rubric Generation
                           |
                           v
                    MongoDB Rubrics
                           |
                           v
                 Rubric-Based Evaluation
                           |
                           v
                 Criterion-wise Marks
                           |
                           v
                    Total Marks
                           |
                    +------+------+
                    |             |
                    v             v
              MongoDB        Evaluation JSON
```

---

# Project Structure

```text
answer-evaluation/
│
├── input_txt/
│   ├── student_1.txt
│   ├── student_2.txt
│   └── ...
│
├── input/
│   ├── student_1.json
│   ├── student_2.json
│   └── ...
│
├── model_answers/
│   ├── model_answers.json
│   └── oop_model_answers.json
│
├── output/
│   ├── dsa_rubrics.json
│   ├── oop_rubrics.json
│   ├── question_mapping_*.json
│   └── evaluation_*.json
│
├── src/
│   ├── __init__.py
│   ├── answer_evaluator.py
│   ├── database.py
│   ├── embeddings.py
│   ├── loader.py
│   ├── main.py
│   ├── mapper.py
│   ├── preprocess.py
│   ├── retrieve.py
│   ├── rubric_generator.py
│   ├── similarity.py
│   ├── subject_detector.py
│   └── txt_to_json.py
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

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Requirements

The project uses Python libraries including:

```text
sentence-transformers
scikit-learn
pymongo
ollama
pytest
```

### Sentence Transformers

Used to generate semantic embeddings for student answers and model-question information.

### Scikit-learn

Used for cosine similarity calculations.

### PyMongo

Used to connect to the local MongoDB database and store mappings, rubrics, and evaluations.

### Ollama

Used to communicate with the local Llama 3.2 model for rubric generation and rubric-based student answer evaluation.

### Pytest

Used for automated testing.

---

# Local LLM Setup

Rubric generation and answer evaluation use the local **Llama 3.2** model through Ollama.

No paid API key is required.

After installing Ollama, download the model:

```powershell
ollama pull llama3.2
```

Verify the model:

```powershell
ollama list
```

Optional manual test:

```powershell
ollama run llama3.2
```

The Python application communicates with the local Ollama service.

Make sure Ollama is running before executing the rubric generation or evaluation pipeline.

---

# MongoDB Setup

The current project uses **local MongoDB**.

The application connects to:

```text
mongodb://localhost:27017/
```

The database is:

```text
answer_evaluation
```

The project uses the following collections:

```text
question_mappings
rubrics
answer_evaluations
```

### question_mappings

Stores the student-to-model question mapping results.

### rubrics

Stores the generated evaluation rubrics.

### answer_evaluations

Stores rubric-based student answer evaluation results.

Make sure MongoDB is running before executing the main pipeline.

---

# Student Input Format

OCR text files are placed inside:

```text
input_txt/
```

The TXT files are converted into question-wise JSON files inside:

```text
input/
```

Example student JSON:

```json
{
    "student": "student_1",
    "answers": {
        "Q1": "In Object Oriented Programming inheritance allows a class to acquire properties and behaviours from another class.",
        "Q2": "Object Oriented Programming is a programming paradigm based on objects that contain data and behaviour.",
        "Q3": "Polymorphism allows a single entity to take multiple forms.",
        "Q4": "A class is a blueprint that defines data and behaviour for objects."
    }
}
```

The `student` field identifies the student.

The `answers` object contains question-wise student answers.

---

# TXT-to-JSON Segmentation

The project includes a TXT parser that converts OCR text into question-wise JSON.

Run:

```powershell
python -m src.txt_to_json
```

The parser supports common OCR question formats such as:

```text
Q1
Q 1
Q.1
Question 1
ANS 10
ANS: 10
Ans ①
Ans ②
1.
2.
3.
4.
1)
2)
1→
2→
1->
2->
```

The parser also handles question markers that appear on the same line as the beginning of the answer.

The segmentation logic is designed to avoid incorrectly treating numbered points inside an answer as new questions.

---

# Model Answer Format

Model answers are stored as JSON files.

## DSA

```text
model_answers/model_answers.json
```

## OOP

```text
model_answers/oop_model_answers.json
```

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
    }
}
```

Each model question contains:

- `question`
- `model_answer`

---

# Subject Detection

Before question mapping, the system compares the student's answers against the DSA and OOP model-answer sets.

The detector calculates semantic scores for both subjects and selects the subject with the stronger score when the configured confidence condition is satisfied.

Possible results include:

```text
DSA
OOP
UNKNOWN
```

If the subject is `UNKNOWN`, the student is not passed to the subject-specific question-mapping stage.

---

# Question Mapping Process

The mapping process works as follows:

```text
Student Answer
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
Threshold Decision
      |
      v
Matched / Unmatched
```

Each student answer is compared against the available model questions.

The candidate with the highest semantic similarity is considered the best candidate.

---

# Semantic Mapping

The system uses a Sentence Transformer model to generate embeddings for student answers and model-question information.

The embeddings are compared using cosine similarity.

Example:

```text
Student Q1 -> Model Q1
similarity = 0.8943
number_match = true
status = matched
```

The system does not require the student answer and model question to use exactly the same words.

Semantic similarity allows different wording to still be mapped to the same question.

---

# Question Number Handling

Question numbers are used as **supporting information**, not as the only mapping decision.

The system can normalize identifiers such as:

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

OCR-specific formats are also handled where possible.

The semantic content is still used to determine whether the student answer corresponds to the model question.

---

# Similarity Thresholds

Current development thresholds are:

```text
Same question number:
similarity >= 0.60

General semantic fallback:
similarity >= 0.70
```

The same-number threshold allows a strong semantic match to be accepted when the question number also agrees.

The general threshold is used when a same-number model question is not available and semantic matching is required.

These are development thresholds. They should be evaluated and calibrated using a larger labelled dataset before being considered production thresholds.

---

# Mapping Status

The system can produce statuses such as:

## `matched`

The selected model question meets the configured similarity threshold.

## `unmatched`

No suitable model question reaches the required similarity threshold.

## `empty_answer`

The student answer is empty.

---

# Example Mapping Output

The generated mapping JSON contains information such as:

```json
{
    "student": "student_1",
    "subject": "OOP",
    "mappings": {
        "Q1": {
            "matched_model_question": "Q1",
            "similarity": 0.8943,
            "number_match": true,
            "threshold_used": 0.6,
            "status": "matched"
        }
    }
}
```

The mapping information includes:

- Student question
- Matched model question
- Similarity score
- Question-number match information
- Threshold used
- Mapping status

---

# Automatic Rubric Generation

The project automatically generates question-wise rubrics from the selected model answers using the local **Llama 3.2** model through Ollama.

The process is:

```text
Model Answer
      |
      v
Local Llama 3.2
      |
      v
Evaluation Criteria
      |
      v
Marks Distribution
      |
      v
Validated Rubric
      |
      v
MongoDB
```

Each rubric contains important evaluation criteria derived from the model answer.

The current implementation uses **10 marks per question** and validates the final mark distribution in Python.

Example:

```json
{
    "question_id": "Q1",
    "question": "Explain inheritance and its types.",
    "criteria": [
        {
            "criterion": "Definition and explanation of inheritance",
            "marks": 2
        },
        {
            "criterion": "Single inheritance",
            "marks": 2
        },
        {
            "criterion": "Multiple inheritance",
            "marks": 2
        }
    ]
}
```

The complete generated rubrics are saved to:

```text
output/dsa_rubrics.json
output/oop_rubrics.json
```

Rubrics are also stored in the MongoDB `rubrics` collection.

If a rubric already exists in MongoDB, the system can retrieve the stored rubric instead of generating it again.

---

# Rubric-Based Student Answer Evaluation

After question mapping and rubric retrieval, the system evaluates each matched student answer against its corresponding rubric.

The evaluation process is:

```text
Student Answer
      |
      v
Matched Model Question
      |
      v
Stored / Generated Rubric
      |
      v
Local Llama 3.2
      |
      v
Criterion-wise Evaluation
      |
      v
Python Validation
      |
      v
Total Marks
```

The evaluator uses the supplied rubric criteria to evaluate the student's answer.

For each criterion, the evaluation records:

- Criterion
- Marks awarded
- Maximum marks
- Reason for the awarded marks

Partial marks are supported.

Python validates the returned marks so that a criterion cannot receive more than its configured maximum.

The current implementation uses:

```text
10 marks per question
```

Example evaluation:

```json
{
    "question_id": "Q1",
    "student_question": "Q1",
    "matched_model_question": "Q1",
    "criteria": [
        {
            "criterion": "Definition of data structure",
            "marks_awarded": 2,
            "max_marks": 2,
            "reason": "The student correctly defines the concept."
        },
        {
            "criterion": "Linear data structures",
            "marks_awarded": 2,
            "max_marks": 3,
            "reason": "The student explains the concept but misses one point."
        }
    ],
    "total_marks": 4,
    "max_marks": 10,
    "evaluation_status": "evaluated"
}
```

The final question score is calculated from the criterion-level marks.

---

# Evaluation Database Storage

Evaluation results are stored in:

```text
answer_evaluation.answer_evaluations
```

Each evaluation document contains:

- Student ID
- Question ID
- Criterion-wise evaluation
- Marks awarded
- Maximum marks
- Total marks
- Evaluation status

The collection uses a unique index on:

```text
student_id
question_id
```

This prevents duplicate evaluation records for the same student and question.

---

# Evaluation JSON Output

The pipeline saves a separate evaluation JSON file for each student:

```text
output/evaluation_student_1.json
output/evaluation_student_2.json
...
```

The student mapping JSON also contains the student's subject, mappings, rubrics, and evaluation result.

Example output files:

```text
output/question_mapping_student_1.json
output/evaluation_student_1.json
```

---

# Multiple Student Support

The system supports multiple students.

Example:

```text
input/
├── student_1.json
├── student_2.json
├── student_3.json
└── ...
```

Each student is processed independently.

MongoDB records are associated with the student ID.

This allows:

- Student-wise mapping
- Student-wise rubric evaluation
- Student-wise marks
- Student-wise retrieval
- Student-wise JSON output

---

# Database Storage

The project uses MongoDB for persistent storage.

## Question Mappings

Stored in:

```text
question_mappings
```

Mappings contain information such as:

- Student ID
- Student question
- Matched model question
- Similarity
- Number match
- Threshold used
- Mapping status

## Rubrics

Stored in:

```text
rubrics
```

Rubrics contain:

- Question ID
- Question
- Evaluation criteria
- Marks distribution

## Evaluations

Stored in:

```text
answer_evaluations
```

Evaluations contain:

- Student ID
- Question ID
- Criterion-wise marks
- Total marks
- Evaluation status

---

# Running the Project

The main pipeline can be executed for a specific student:

```powershell
python -m src.main student_1
```

The complete pipeline performs:

```text
1. Load Student JSON
2. Detect Subject
3. Select DSA/OOP Model Answers
4. Generate Semantic Embeddings
5. Map Student Questions
6. Save Question Mappings
7. Retrieve or Generate Rubrics
8. Evaluate Student Answers
9. Calculate Criterion-wise Marks
10. Calculate Total Marks
11. Save Evaluations to MongoDB
12. Generate Output JSON Files
```

---

# Running Without a Student ID

If the project supports processing all available student files, run:

```powershell
python -m src.main
```

This processes the available `student_*.json` files according to the implementation in `src/main.py`.

---

# Example Result

A successful evaluation can produce results such as:

```text
RUBRIC-BASED ANSWER EVALUATION

Evaluating Q1 against rubric...
[EVALUATION] Q1: 10/10

Evaluating Q2 against rubric...
[EVALUATION] Q2: 6/10

Evaluating Q3 against rubric...
[EVALUATION] Q3: 8/10

Evaluating Q4 against rubric...
[EVALUATION] Q4: 10/10

[TOTAL] student_1: 34/40
```

The exact marks depend on the student's answers and the generated/stored rubrics.

---

# Testing

Run the test suite using:

```powershell
pytest
```

The project includes tests for components such as:

- Database operations
- Database retrieval
- File loading
- Question mapping
- Text preprocessing
- Semantic mapping
- Similarity calculation

The rubric generation and answer evaluation stages also depend on the local Ollama/Llama 3.2 service when they are executed as part of the main pipeline.

---

# Current Scope

The current implementation covers:

1. Student answer loading
2. OCR text preprocessing
3. TXT-to-JSON conversion
4. Question-wise segmentation
5. Subject detection
6. Semantic embedding generation
7. Question-to-question semantic mapping
8. Cosine similarity calculation
9. Similarity threshold decisions
10. MongoDB database storage
11. Student-wise mapping retrieval
12. Automatic rubric generation
13. Local Llama 3.2 / Ollama integration
14. MongoDB rubric storage
15. Rubric-based student answer evaluation
16. Criterion-wise marks calculation
17. Total marks calculation
18. MongoDB evaluation storage
19. Student-wise evaluation JSON output
20. Automated testing

The project currently does **not** implement:

- AI-based feedback generation
- Web/API interface
- Student dashboard

---

# Future Scope

Planned improvements include:

- AI-based feedback generation
- Personalized feedback for each student
- Suggestions for improving individual answers
- Web/API interface
- Student dashboard
- Teacher dashboard
- Larger labelled evaluation datasets
- Threshold calibration using real evaluation data
- Additional academic subjects
- More robust OCR error handling
- Production deployment

---

# Team

The project is developed as an academic AI-based answer evaluation system.

---

# Project Status

The project currently covers:

```text
OCR Student Answers
        +
TXT-to-JSON Conversion
        +
Subject Detection
        +
Semantic Question Mapping
        +
MongoDB Mapping Storage
        +
Automatic Rubric Generation
        +
MongoDB Rubric Storage
        +
Rubric-Based Answer Evaluation
        +
Criterion-wise Marks
        +
Total Marks
        +
MongoDB Evaluation Storage
        +
Evaluation JSON Output
```

The current development stage covers **reliable question mapping, automatic rubric generation, and rubric-based student answer evaluation**.

The next planned stage is **AI-based feedback generation**, where the evaluated results can be converted into meaningful feedback and improvement suggestions for students.

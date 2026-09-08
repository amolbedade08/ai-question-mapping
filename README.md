# AI Question Mapping Project


## Overview


This project maps OCR-extracted student answers to the corresponding questions in a model-answer document using semantic similarity.

The system is focused specifically on the **question-mapping stage** of an automated answer-processing pipeline. It does **not** currently perform answer grading, marks calculation, rubric evaluation, or AI-based feedback generation.

### Current capabilities


- OCR-extracted student answers
- TXT-to-question-wise JSON conversion
- Question-wise student JSON files
- DSA and OOP model-answer sets
- Automatic subject detection between DSA and OOP
- Semantic question mapping using Sentence Transformers
- Question-number normalization and supporting number matching
- Similarity thresholds for matched/unmatched decisions
- Multiple-student processing
- Local MongoDB storage
- Student-wise mapping retrieval
- Automatic rubric generation from model answers
- Local Llama 3.2 model through Ollama
- MongoDB rubric storage
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

Instead, it uses **semantic similarity** to compare student answer content with model-question information and identify the most relevant model question.

For example, a student may write:

```
A child class can inherit properties and methods from a parent class.

```

**svg**

while the model question information may describe:

```
Inheritance is the OOP mechanism by which a derived class
acquires the properties and behaviours of a base class.

```

**svg**

Although the wording is different, semantic embeddings can identify that both refer to inheritance.

---

# Project Architecture


```
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
       +--------------------+
       |                    |
       v                    v
      DSA                  OOP
       |                    |
       +---------+----------+
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
                 +-------------------+
                 |                   |
                 v                   v
          MongoDB Mapping      Model Answer
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
       Student-wise Retrieval

```

**svg**

---

# Project Structure


```
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
│   └── question_mapping_*.json
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

**svg**

---

# Installation


Create a virtual environment:

```
python -m venv .venv
```

**svg**

## Windows


```
.venv\Scripts\activate
```

**svg**

## Linux/macOS


```
source .venv/bin/activate
```

**svg**

Install dependencies:

```
pip install -r requirements.txt
```

**svg**

---

# Requirements


The project uses Python libraries including:

```
sentence-transformers
scikit-learn
pymongo
ollama
pytest

```

**svg**

Sentence Transformers is used to generate semantic embeddings.

Cosine similarity is used to compare the generated embeddings.

PyMongo is used to connect to the local MongoDB database.

Ollama is used to communicate with the local Llama 3.2 model for automatic rubric generation.

---


# Local LLM Setup

Rubric generation uses the local **Llama 3.2** model through Ollama. No paid API key is required.

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

The Python application uses the local Ollama service when a rubric is missing from MongoDB.

---

# MongoDB Setup


The current project uses **local MongoDB**, not MongoDB Atlas.

The application connects to:

```
mongodb://localhost:27017/

```

**svg**

The database is:

```
answer_evaluation

```

**svg**

The mapping collection is:

```
question_mappings

```

The rubric collection is:

```
rubrics

```

**svg**

Make sure MongoDB is running before executing the main pipeline or retrieving stored mappings.

---

# Student Input Format


OCR text files are placed inside:

```
input_txt/

```

**svg**

The TXT files are converted into question-wise JSON files inside:

```
input/

```

**svg**

Example JSON:

```
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

**svg**

The `student` field identifies the student.

The `answers` object contains the question-wise student answers.

---

# TXT-to-JSON Segmentation


The project includes a TXT parser that converts OCR text into question-wise JSON.

Run:

```
python -m src.txt_to_json
```

**svg**

The parser supports common OCR question formats such as:

```
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

**svg**

The parser also handles question markers that appear on the same line as the beginning of the answer.

The segmentation logic is designed to avoid incorrectly treating numbered points inside an answer as new questions.

---

# Model Answer Format


Model answers are stored as JSON files.

## DSA


```
model_answers/model_answers.json

```

**svg**

## OOP


```
model_answers/oop_model_answers.json

```

**svg**

Example:

```
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

**svg**

---

# Subject Detection


Before question mapping, the system compares the student's answers against the DSA and OOP model-answer sets.

The detector calculates semantic scores for both subjects and selects the subject with the stronger score when the configured confidence condition is satisfied.

Possible results include:

```
DSA
OOP
UNKNOWN

```

**svg**

If the subject is `UNKNOWN`, the student is not passed to the subject-specific question-mapping stage.

---

# Question Mapping Process


The mapping process works as follows:

```
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

**svg**

Each student answer is compared against the available model questions.

The candidate with the highest semantic similarity is considered the best candidate.

---

# Semantic Mapping


The system uses a Sentence Transformer model to generate embeddings for student answers and model-question information.

The embeddings are compared using cosine similarity.

For example:

```
Student Q1 -> Model Q1
similarity = 0.8943
number_match = true
status = matched

```

**svg**

The system does not require the student answer and model question to use exactly the same words.

Semantic similarity allows different wording to still be mapped to the same question.

---

# Question Number Handling


Question numbers are used as **supporting information**, not as the only mapping decision.

The system can normalize identifiers such as:

```
Q1
Q 1
Q.1
Question 1
1

```

**svg**

into:

```
Q1

```

**svg**

OCR-specific formats are also handled where possible.

The semantic content is still used to determine whether the student answer corresponds to the model question.

---

# Similarity Thresholds


Current development thresholds are:

```
Same question number:
similarity >= 0.60

General semantic fallback:
similarity >= 0.70

```

**svg**

The same-number threshold allows a strong semantic match to be accepted when the question number also agrees.

The general threshold is used when a same-number model question is not available and semantic matching is required.

These are development thresholds. They should be evaluated and calibrated using a larger labelled dataset before being considered production thresholds.

---

# Mapping Status


The system can produce statuses such as:

### `matched`


The selected model question meets the configured similarity threshold.

### `unmatched`


No suitable model question reaches the required similarity threshold.

### `empty_answer`


The student answer is empty.

---

# Example Mapping Output


The generated mapping JSON contains information such as:

```
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

**svg**

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

Each rubric contains important evaluation criteria derived from the model answer. The current implementation uses **10 marks per question** and validates the final mark distribution in Python.

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
        },
        {
            "criterion": "Multilevel inheritance",
            "marks": 2
        },
        {
            "criterion": "Hierarchical and Hybrid inheritance",
            "marks": 2
        }
    ],
    "total_marks": 10
}
```

Rubrics are generated for both DSA and OOP model-answer sets.

Generated JSON files:

```text
output/dsa_rubrics.json
output/oop_rubrics.json
```

Rubrics are also stored in the MongoDB `rubrics` collection.

If a rubric already exists in MongoDB, the main pipeline retrieves it instead of unnecessarily generating it again with the local LLM.

---

# Rubric Database Storage

Rubrics are stored in:

```text
answer_evaluation.rubrics
```

Each rubric document contains:

- Subject
- Question ID
- Question text
- Evaluation criteria
- Marks per criterion
- Total marks

Example document:

```json
{
    "subject": "DSA",
    "question_id": "Q1",
    "question": "Explain data structures and their types.",
    "criteria": [
        {
            "criterion": "Definition of data structure",
            "marks": 2
        }
    ],
    "total_marks": 10
}
```

The `question_mappings` collection stores the question-mapping results separately.

---

# Multiple Student Support


The system supports processing multiple student files.

For example:

```
input_txt/
├── student_1.txt
├── student_2.txt
├── student_3.txt
├── student_4.txt
├── student_5.txt
├── student_6.txt
└── student_7.txt

```

**svg**

Each student's data is processed independently.

The student ID is also stored with the mapping in MongoDB.

---

# Database Storage


Mapping results are currently stored in **local MongoDB**.

Connection:

```
mongodb://localhost:27017/

```

**svg**

Database:

```
answer_evaluation

```

**svg**

Collection:

```
question_mappings

```

**svg**

Mappings are associated with the student ID and student question.

This allows mappings to be stored and retrieved without rerunning the semantic mapping process.

---

# Database Retrieval


To retrieve mappings for a student:

```
python -m src.retrieve student_1
```

**svg**

Example output:

```
Mappings for student_1:

Q1 -> Q1 | similarity=0.8943 | status=matched
Q2 -> Q2 | similarity=0.8477 | status=matched
Q3 -> Q3 | similarity=0.8788 | status=matched
Q4 -> Q4 | similarity=0.8582 | status=matched

```

**svg**

Replace the student ID with the required student.

For example:

```
python -m src.retrieve student_6
```

**svg**

---

# Running the Project


## Step 1: Prepare OCR TXT files


Place student OCR text files inside:

```
input_txt/

```

**svg**

## Step 2: Convert TXT files to JSON


Run:

```
python -m src.txt_to_json
```

**svg**

The generated files will be placed inside:

```
input/

```

**svg**

## Step 3: Start MongoDB


The project expects a local MongoDB server at:

```
mongodb://localhost:27017/

```

**svg**

## Step 4: Run the main pipeline


Process one student:

```powershell
python -m src.main student_1
```

Process another specific student:

```powershell
python -m src.main student_6
```

Process all students:

```powershell
python -m src.main
```

When a specific student ID is supplied, only that student's mapping and rubric pipeline is processed. Without a student ID, all `student_*.json` files are processed.

**svg**

The pipeline performs:

```
Load student JSON
        |
        v
Subject Detection
        |
        v
Select DSA/OOP model
        |
        v
Semantic Question Mapping
        |
        v
Save Mapping to MongoDB
        |
        v
Generate Mapping Output

```

**svg**

---

# Testing


Run the complete test suite:

```
pytest -v
```

**svg**

The test suite covers areas including:

- Database storage
- Database retrieval
- Student JSON loading
- Model answer loading
- Question mapping
- Incorrect question mapping
- Text preprocessing
- Semantic mapping
- Semantic similarity

---

# Example Result


For the OOP sample data, the semantic mapper previously produced results such as:

```
Student Q1 -> Model Q1 | similarity=0.8943 | number_match=True | threshold=0.60 | status=matched

Student Q2 -> Model Q2 | similarity=0.8477 | number_match=True | threshold=0.60 | status=matched

Student Q3 -> Model Q3 | similarity=0.8788 | number_match=True | threshold=0.60 | status=matched

Student Q4 -> Model Q4 | similarity=0.8582 | number_match=True | threshold=0.60 | status=matched

```

**svg**

These scores demonstrate semantic mapping behaviour on the sample data.

They should not be interpreted as overall model accuracy. Proper accuracy measurement requires a larger labelled dataset containing known correct and incorrect mappings.

---

# Current Scope


The current implementation focuses on:

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
12. Automated testing

The project currently does **not** perform:

- Answer grading
- Marks calculation
- Rubric evaluation
- Answer-quality scoring
- AI-based feedback generation

---

# Future Scope


The broader planned pipeline can be extended as follows:

```
OCR Extraction
      |
      v
Answer Segmentation
      |
      v
Subject Detection
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

**svg**

Possible future improvements include:

- Improved OCR handling
- More robust question segmentation
- Larger DSA and OOP datasets
- Mapping accuracy evaluation
- Better threshold calibration
- Criterion-level answer comparison after question mapping
- Rubric-based student answer evaluation
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

The current implementation supports:

```text
OCR TXT Input
      +
Question-wise JSON Conversion
      +
DSA / OOP Subject Detection
      +
Subject-specific Model Selection
      +
Semantic Question Mapping
      +
Multiple Students
      +
MongoDB Mapping Storage
      +
Automatic Rubric Generation
      +
Local Llama 3.2 / Ollama
      +
MongoDB Rubric Storage
      +
Student-wise Retrieval
      +
Automated Testing
```

The current development stage covers **reliable question mapping and automatic rubric generation**.

The next stage is **rubric-based student answer evaluation**, where the mapped student answer will be compared against the generated rubric to award criterion-wise marks.

---

# Team

- Chaitanya Kulkarni
- Shashank Gangade
- Amol Bedade

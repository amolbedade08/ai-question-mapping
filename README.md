Question Mapping Project

Overview

This project maps OCR-extracted student answers to the corresponding questions in a model answer document using semantic similarity. The project is intentionally limited to the question-mapping step of the document-processing pipeline and does not include answer evaluation, marks calculation, rubric evaluation, or AI-based grading.


The system accepts:

OCR-extracted student answers in JSON format

A model answer JSON containing questions and reference answers


It compares the student answers with the model questions and identifies the most relevant model question.

Purpose

OCR extraction can introduce incorrect question numbers, OCR mistakes, different numbering formats, questions appearing in a different order, and differences in student and model-answer wording.


Therefore, the system does not rely only on question numbers. It uses semantic similarity to compare student answer content with model-question information and identifies the most relevant model question.

Project Structure

project/

    input/

        student1.json

    model_answers/

        model_answers.json

    output/

        question_mapping_student1.json

    tests/

        test_loader.py

        test_mapper.py

        test_preprocess.py

        test_similarity.py

    src/

        main.py

        mapper.py

        loader.py

        preprocess.py

        embeddings.py

        similarity.py

    requirements.txt

    README.md

Installation

cd project

python -m venv .venv


Windows:

.venv\Scripts\activate


Linux/macOS:

source .venv/bin/activate


pip install -r requirements.txt

Requirements

The project uses Python libraries for semantic text comparison and testing:


sentence-transformers

scikit-learn

pytest

How to Run

Place the student answer JSON file inside the input/ folder and the model answer JSON file inside the model_answers/ folder.


Then run:


python -m src.main


The program loads the student answers and model answers, generates semantic embeddings, compares the student answers against all model questions, and saves the mapping result inside the output/ folder.

Student Input Format

{

    "student": "student1",

    "answers": {

        "Q1": "In Object Oriented Programming inheritance allows a class to acquire properties and behaviours from another class.",

        "Q2": "Object Oriented Programming is a programming paradigm based on objects that contain data and behaviour.",

        "Q3": "Polymorphism allows a single entity to take multiple forms.",

        "Q4": "A class is a blueprint that defines data and behaviour for objects."

    }

}

Model Answer Format

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

Mapping Process

Student Answers

      |

      v

Text Preprocessing

      |

      v

Semantic Embedding

      |

      v

Compare with Model Questions

      |

      v

Cosine Similarity

      |

      v

Best Candidate

      |

      v

Matched / Unmatched

Output Format

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

Mapping Status

matched

unmatched

empty_answer


matched means the similarity score meets the configured threshold.


unmatched means no model question has sufficient similarity to confidently map the student question.


empty_answer means the student answer is empty.

Similarity Threshold

Same question number:

similarity >= 0.60


Different or uncertain question number:

similarity >= 0.70


Question numbers are not used as the only mapping criteria. Semantic similarity is used to determine the relevance of the student answer to the model question.


These thresholds are development values and require further testing with larger datasets before production use.

OCR Handling

OCR extraction may produce incorrect question numbers.


Example:


Actual:

Q1


OCR:

Q1991


The mapper does not depend only on the question number. It compares the semantic content against the available model questions and can identify a possible corresponding model question when the similarity is sufficiently high.

Example Result

For the OOP sample paper, the system produced:


Student Q1 -> Model Q1 | similarity=0.8943 | status=matched

Student Q2 -> Model Q2 | similarity=0.8477 | status=matched

Student Q3 -> Model Q3 | similarity=0.8788 | status=matched

Student Q4 -> Model Q4 | similarity=0.8582 | status=matched

Testing

Run all tests using:


pytest -v


The current test suite covers:

Student JSON loading

Model answer loading

Text preprocessing

Semantic similarity

Correct question mapping

Incorrect question mapping

Unmatched question detection


Current test result:

8 passed

Notes

UTF-8 JSON input is supported.

Semantic embeddings are generated using a sentence-transformer model.

Cosine similarity is used for semantic comparison.

Student questions are compared against all available model questions.

Question numbers are used as supporting information and not as the only mapping decision.

Unrelated questions are not forcefully mapped when similarity is below the configured threshold.

The current implementation is limited to question mapping.

Answer evaluation, rubric evaluation, marks calculation, and feedback generation are not included.

Future Scope

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


The current project focuses only on the Question Mapping stage.

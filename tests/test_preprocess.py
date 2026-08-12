from src.preprocess import (
    normalize_text,
    preprocess_answer
)


def test_normalize_text():

    text = """
    Python   is   a programming language.
    
    
    It is readable.
    """

    result = normalize_text(text)

    assert "Python is a programming language." in result


def test_remove_ocr_noise():

    text = """
    Python is a language.

    End of sample
    Page 12
    OCR scan quality medium
    """

    result = preprocess_answer(text)

    assert "Python is a language." in result
    assert "End of sample" not in result
    assert "Page 12" not in result
import re


def split_into_chunks(text):
    """
    Split an answer into semantic chunks.

    We first split paragraphs and then sentences.
    """

    if not text:
        return []

    paragraphs = re.split(
        r"\n\s*\n",
        text
    )

    chunks = []

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        sentences = re.split(
            r"(?<=[.!?])\s+",
            paragraph
        )

        for sentence in sentences:

            sentence = sentence.strip()

            if sentence:
                chunks.append(sentence)

    return chunks
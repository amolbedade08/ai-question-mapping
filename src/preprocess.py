import re


def normalize_text(text):
    """
    Basic OCR text normalization.

    We deliberately keep the text content intact.
    """

    if not text:
        return ""

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    # Normalize spaces and tabs.
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Remove excessive blank lines.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def remove_obvious_noise(text):
    """
    Remove obvious OCR/page noise.

    We do NOT aggressively clean the text because
    technical words may be important for semantic mapping.
    """

    if not text:
        return ""

    lines = text.splitlines()

    cleaned = []

    noise_patterns = [
        r"^page\s+\d+$",
        r"^end\s+of\s+sample$",
        r"^continued\s+on\s+next\s+page$",
        r"^ocr\s+scan\s+quality.*$"
    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        is_noise = False

        for pattern in noise_patterns:

            if re.match(
                pattern,
                line,
                re.IGNORECASE
            ):
                is_noise = True
                break

        if not is_noise:
            cleaned.append(line)

    return "\n".join(cleaned)


def preprocess_answer(text):

    text = normalize_text(text)

    text = remove_obvious_noise(text)

    return text
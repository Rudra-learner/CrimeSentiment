import re


def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    text = text.strip()

    return text
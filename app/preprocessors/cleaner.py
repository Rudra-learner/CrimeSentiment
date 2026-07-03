import re


REMOVE_PATTERNS = [

    r"also read.*",
    r"read also.*",
    r"read more.*",
    r"click here.*",
    r"advertisement.*",
    r"advertisement",
    r"advertisment.*",
    r"follow us.*",
    r"join our.*",
    r"subscribe.*",
    r"share this.*",
    r"watch video.*",
    r"image source.*",
    r"photo credit.*",
    r"representative image.*",
    r"copyright.*",
    r"©.*",
    r"all rights reserved.*",
    r"whatsapp channel.*",
    r"telegram channel.*",
    r"facebook.*",
    r"instagram.*",
    r"twitter.*",
    r"youtube.*",
    r"https?://\S+",
    r"www\.\S+"

]


def clean_text(text):

    if not text:
        return ""

    text = str(text)

    
    text = re.sub(r"<[^>]+>", " ", text)

    
    text = re.sub(r"https?://\S+", " ", text)

    # Remove Emails
    text = re.sub(r"\S+@\S+", " ", text)

    
    for pattern in REMOVE_PATTERNS:

        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE
        )

    
    text = re.sub(r"\s+", " ", text)

    return text.strip()
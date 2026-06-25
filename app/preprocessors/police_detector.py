POLICE_KEYWORDS = [

    "police",
    "iic",
    "sp",
    "dsp",
    "crime branch",
    "investigation"
]


def police_mentioned(text):

    text = text.lower()

    for keyword in POLICE_KEYWORDS:

        if keyword in text:
            return True

    return False
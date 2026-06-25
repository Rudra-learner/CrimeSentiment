LOCATIONS = [

    "nayagarh",
    "ranpur",
    "sarankul",
    "odagaon",
    "daspalla",
    "nuagaon",
    "khandapada",
    "gania",
    "bhapur",
    "kantilo"
]


def detect_location(text):

    text = text.lower()

    for location in LOCATIONS:

        if location in text:
            return location.title()

    return "Unknown"
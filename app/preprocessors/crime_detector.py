CRIME_KEYWORDS = {

    "MURDER": [
        "murder",
        "killed",
        "homicide"
    ],

    "THEFT": [
        "theft",
        "stolen",
        "loot"
    ],

    "ROBBERY": [
        "robbery",
        "robbed"
    ],

    "CYBER_FRAUD": [
        "cyber fraud",
        "online scam",
        "fraud"
    ],

    "RAPE": [
        "rape",
        "sexual assault"
    ],

    "KIDNAPPING": [
        "kidnap",
        "abduction"
    ],

    "ACCIDENT": [
        "accident",
        "collision"
    ]
}


def detect_crime(text):

    text = text.lower()

    for crime, keywords in CRIME_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:
                return crime

    return "OTHER"
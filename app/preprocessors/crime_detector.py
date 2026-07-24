from app.preprocessors.macro_micro_crimes import (
    MACRO_CRIMES,
    MICRO_CRIMES
)


def normalize_text(text):
    """
    Normalize text for matching.
    """
    return " ".join(text.lower().split())


def calculate_score(text, keywords):
    """
    Calculate weighted score for a list of keywords.

    Weighting:
        Single-word keyword  -> 1
        Two-word phrase      -> 2
        Three+ word phrase   -> 3
    """

    score = 0

    for keyword in keywords:

        keyword = keyword.lower().strip()

        if keyword in text:

            words = len(keyword.split())

            if words >= 3:
                score += 3

            elif words == 2:
                score += 2

            else:
                score += 1

    return score


def detect_macro_crime(text):
    """
    Detect the most likely macro crime.
    """

    text = normalize_text(text)

    crime_scores = {}

    for macro, keywords in MACRO_CRIMES.items():

        crime_scores[macro] = calculate_score(text, keywords)

    best_macro = max(crime_scores, key=crime_scores.get)

    if crime_scores[best_macro] == 0:
        return "OTHER"

    return best_macro


def detect_micro_crime(text, macro_crime):
    """
    Detect the best micro crime under the detected macro.
    """

    text = normalize_text(text)

    if macro_crime not in MICRO_CRIMES:
        return macro_crime

    micro_scores = {}

    for micro, keywords in MICRO_CRIMES[macro_crime].items():

        micro_scores[micro] = calculate_score(text, keywords)

    if not micro_scores:
        return macro_crime

    best_micro = max(micro_scores, key=micro_scores.get)

    if micro_scores[best_micro] == 0:
        return macro_crime

    return best_micro


def detect_crime(text):
    """
    Detect both macro and micro crime.

    Returns:
    {
        "macro_crime": "...",
        "micro_crime": "..."
    }
    """

    macro = detect_macro_crime(text)

    if macro == "OTHER":

        return {

            "macro_crime": "OTHER",

            "micro_crime": "OTHER"

        }

    micro = detect_micro_crime(text, macro)

    return {

        "macro_crime": macro,

        "micro_crime": micro

    }
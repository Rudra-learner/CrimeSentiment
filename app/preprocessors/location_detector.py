from app.preprocessors.odisha_gazetteer import ODISHA_LOCATIONS


def detect_location(text):
    """
    Detect the Odisha district from the article.

    Returns:
        str : District name
        or "Unknown"
    """

    text = text.lower()

    best_district = "Unknown"
    max_score = 0

    for district, locations in ODISHA_LOCATIONS.items():

        score = 0

        # Match district name
        if district.lower() in text:
            score += text.count(district.lower())

        # Match every English/Odia synonym
        for location_group in locations:

            for name in location_group:

                if name.lower() in text:
                    score += text.count(name.lower())

        if score > max_score:
            max_score = score
            best_district = district

    return best_district
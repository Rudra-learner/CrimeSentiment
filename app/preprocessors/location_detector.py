LOCATIONS = [

    "nayagarh",
    "ନୟାଗଡ଼",
    "ranpur",
    "ରଣପୁର",
    "sarankul",
    "ସରାଙ୍କୁଳ",
    "odagaon",
    "ଓଡ଼ଗାଁ",
    "daspalla",
    "ଦଶପଲ୍ଲା",
    "nuagaon",
    "khandapada",
    "ଖଣ୍ଡପଡା",
    "gania",
    "ଗଣିଆ",
    "bhapur",
    "ଭାପୁର",
    "fategarh",
    "banigochha",
    "ବାଣିଗୋଛା",
    "kantilo",
    "କଣ୍ଟିଲୋ",
    "itamati",
    "fategarh police",
    "nayagarh police"
]

POLICE_STATION_MAPPING = {

    "Odagaon Police Station": "Nayagarh",

    "Sarankul Police Station": "Nayagarh",

    "Ranpur Police Station": "Nayagarh",

    "Nuagaon Police Station": "Nayagarh",

    "Daspalla Police Station": "Nayagarh",

    "Fategarh Police Station": "Nayagarh",

    "Khandapada Police Station": "Nayagarh",

    "Itamati Police Station": "Nayagarh"

}


def detect_location(text):

    text_lower = text.lower()

    scores = {}

    for location in LOCATIONS:

        count = text_lower.count(location.lower())

        if count > 0:

            scores[location] = count

    if not scores:

        return "Unknown"

    best_location = max(

    scores,

    key=scores.get

)

    return POLICE_STATION_MAPPING.get(

    best_location,

    best_location

)
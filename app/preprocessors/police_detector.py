from app.preprocessors.odisha_gazetteer import ODISHA_LOCATIONS

POLICE_KEYWORDS = [

    # General Police
    "police",
    "police station",
    "police team",
    "police personnel",
    "law enforcement",
    "investigating officer",

    # Police Organizations
    "crime branch",
    "cid",
    "cbi",
    "stf",
    "special task force",
    "eow",
    "economic offences wing",
    "vigilance",
    "railway police",
    "traffic police",

    # Police Designations
    "dgp",
    "adg",
    "ig",
    "dig",
    "sp",
    "additional sp",
    "asp",
    "sdpo",
    "dsp",
    "inspector",
    "inspector in charge",
    "iic",
    "sho",
    "oc",
    "si",
    "sub inspector",
    "asi",
    "assistant sub inspector",
    "head constable",
    "constable",

    # Investigation
    "investigation",
    "probe",
    "raid",
    "search operation",
    "custody",
    "interrogation",
    "chargesheet",

    # Arrest
    "arrest",
    "arrested",
    "detained",
    "held",
    "nabbed",
    "apprehended",
    "seized",

    # Odisha Police
    "odisha police",
    "nayagarh police",

    # Odia Keywords
    "ପୋଲିସ",
    "ଥାନା",
    "ପୋଲିସ ଥାନା",
    "ଅପରାଧ ଶାଖା",
    "କ୍ରାଇମ ବ୍ରାଞ୍ଚ",
    "ସିଆଇଡି",
    "ସିବିଆଇ",
    "ଭିଜିଲାନ୍ସ",
    "ତଦନ୍ତ",
    "ଗିରଫ",
    "ଅଟକ",
    "ଜବତ",
    "ପଚରାଉଚରା",
    "ଏସପି",
    "ଡିଏସପି",
    "ଆଇଆଇସି",
    "ଏସଆଇ",
    "ଏଏସଆଇ"

]


def police_mentioned(text):

    if not text:
        return False

    text = text.lower()

    # Check if any police keyword exists
    police_found = any(
        keyword.lower() in text
        for keyword in POLICE_KEYWORDS
    )

    # Check if any Odisha district or place exists
    location_found = False

    for district, places in ODISHA_LOCATIONS.items():

    # Check district name
        if district.lower() in text:
            location_found = True
            break

    # Check every English/Odia synonym
        for place_group in places:

            for place in place_group:

                if place.lower() in text:
                    location_found = True
                    break

            if location_found:
                break

        if location_found:
                break

    return police_found 
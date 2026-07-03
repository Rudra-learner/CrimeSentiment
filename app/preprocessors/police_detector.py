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

    text = text.lower()

    matches = 0

    for keyword in POLICE_KEYWORDS:

        if keyword.lower() in text:

            matches += 1

    return matches > 0
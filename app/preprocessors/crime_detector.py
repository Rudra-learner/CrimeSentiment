CRIME_KEYWORDS = {

    "MURDER": [

        # English
        "murder",
        "killed",
        "homicide",
        "slain",
        "dead body",
        "body recovered",
        "body found",
        "hacked to death",
        "shot dead",
        "strangled",
        "death mystery",

        # Odia
        "ହତ୍ୟା",
        "ହତ୍ୟାକାଣ୍ଡ",
        "ଖୁନ",
        "ମୃତଦେହ",
        "ଶବ",
        "ଶବ ଉଦ୍ଧାର",
        "ହତ"
    ],

    "THEFT": [

        "theft",
        "stolen",
        "steal",
        "thief",
        "burglary",
        "house break",
        "housebreaking",

        "ଚୋରି",
        "ଚୋର",
        "ଚୋରାଇ",
        "ଘର ଭାଙ୍ଗି"
    ],

    "ROBBERY": [

        "robbery",
        "robbed",
        "loot",
        "looted",
        "snatching",
        "dacoity",

        "ଲୁଟ",
        "ଲୁଟପାଟ",
        "ଡକାୟତି",
        "ଛିନତାଇ"
    ],

    "CYBER_FRAUD": [

        "cyber fraud",
        "cyber crime",
        "online fraud",
        "online scam",
        "upi fraud",
        "atm fraud",
        "otp fraud",
        "digital arrest",
        "money mule",
        "phishing",
        "hacking",

        "ସାଇବର",
        "ସାଇବର ଠକେଇ",
        "ଅନଲାଇନ ଠକେଇ",
        "ୟୁପିଆଇ",
        "ଏଟିଏମ ଠକେଇ"
    ],

    "FRAUD": [

        "fraud",
        "cheating",
        "cheated",
        "forgery",
        "scam",

        "ଠକେଇ",
        "ପ୍ରତାରଣା",
        "ଜାଲିଆତି"
    ],

    "KIDNAPPING": [

        "kidnap",
        "kidnapped",
        "abduction",
        "abducted",
        "missing child",

        "ଅପହରଣ",
        "ନିଖୋଜ"
    ],

    "RAPE": [

        "rape",
        "sexual assault",
        "sexual abuse",
        "molestation",

        "ଦୁଷ୍କର୍ମ",
        "ବଳାତ୍କାର",
        "ଯୌନ ଉତ୍ପୀଡନ"
    ],

    "ASSAULT": [

        "attack",
        "assault",
        "beaten",
        "stabbed",
        "injured",
        "violence",

        "ଆକ୍ରମଣ",
        "ମାଡ଼",
        "ଛୁରିମାଡ଼",
        "ଆହତ"
    ],

    "DRUG": [

        "ganja",
        "brown sugar",
        "drug",
        "narcotics",
        "drug peddler",

        "ଗଞ୍ଜେଇ",
        "ବ୍ରାଉନ ସୁଗର",
        "ମାଦକ"
    ],

    "ARMS": [

        "gun",
        "pistol",
        "firearm",
        "rifle",
        "weapon",
        "illegal weapon",

        "ବନ୍ଧୁକ",
        "ପିସ୍ତଲ",
        "ଅସ୍ତ୍ର"
    ],

    "ACCIDENT": [

        "accident",
        "road accident",
        "collision",
        "electrocution",
        "crash",

        "ଦୁର୍ଘଟଣା",
        "ବିଦ୍ୟୁତ ଆଘାତ",
        "ସଡ଼କ ଦୁର୍ଘଟଣା"
    ],

    "SUICIDE": [

        "suicide",
        "attempted suicide",
        "self immolation",
        "hanged",
        "consumed poison",

        "ଆତ୍ମହତ୍ୟା",
        "ଫାଶୀ",
        "ବିଷ ପିଇ"
    ],

    "MISSING": [

        "missing",
        "missing person",
        "missing woman",
        "missing boy",
        "missing girl",

        "ନିଖୋଜ",
        "ବେପତ୍ତା"
    ]

}

def detect_crime(text):

    text = text.lower()

    crime_scores = {}

    for crime, keywords in CRIME_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword.lower() in text:

                score += 1

        crime_scores[crime] = score

    best_crime = max(
        crime_scores,
        key=crime_scores.get
    )

    if crime_scores[best_crime] == 0:

        return "OTHER"

    return best_crime
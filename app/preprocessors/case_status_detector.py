SOLVED_KEYWORDS = [

    # Arrest
    "arrested",
    "held",
    "apprehended",
    "detained",
    "taken into custody",
    "nabbed",
    "caught",
    "captured",

    # Case solved
    "case solved",
    "crime solved",
    "police solved",
    "cracked",
    "identified",

    # Court
    "chargesheet filed",
    "charge sheet filed",
    "chargesheet submitted",
    "convicted",
    "sentenced",
    "found guilty",

    # All accused
    "all accused arrested",
    "all accused held",

    # English
    "case cracked",
    "mastermind arrested",

    # Odia
    "ଗିରଫ",
    "ଗିରଫତାର",
    "ଧରାପଡିଲେ",
    "ଅଭିଯୁକ୍ତ ଗିରଫ",
    "ଦୋଷୀ",
    "ଦଣ୍ଡିତ",
    "ଚାର୍ଜସିଟ",
    "ମାମଲା ସମାଧାନ"

]

ONGOING_KEYWORDS = [

    "investigation",
    "under investigation",
    "probe",
    "probe underway",
    "investigating",
    "search operation",
    "search underway",
    "questioning",
    "interrogation",
    "forensic examination",
    "evidence collection",
    "examining cctv",
    "cctv footage",
    "awaiting report",
    "manhunt",
    "looking into",
    "crime branch investigating",
    "further investigation",

    # English
    "police investigating",
    "investigation continues",

    # Odia
    "ତଦନ୍ତ",
    "ଅନୁସନ୍ଧାନ",
    "ଯାଞ୍ଚ",
    "ତଦନ୍ତ ଜାରି",
    "ପଚରାଉଚରା",
    "ସନ୍ଧାନ",
    "ଖୋଜାଖୋଜି"

]

UNSOLVED_KEYWORDS = [

    "unknown accused",
    "unidentified",
    "absconding",
    "on the run",
    "yet to be traced",
    "no clue",
    "no breakthrough",
    "could not trace",
    "could not identify",
    "search continues",
    "accused escaped",
    "escaped",
    "fled",
    "not arrested",

    # Missing
    "missing",
    "still missing",

    # Odia
    "ଅଜଣା",
    "ଅଜ୍ଞାତ",
    "ଫେରାର",
    "ନିଖୋଜ",
    "ଧରାପଡିନାହିଁ",
    "ଖୋଜା ଚାଲିଛି"

]

PARTIALLY_SOLVED_KEYWORDS = [

    "one accused arrested",
    "two accused arrested",
    "three accused arrested",
    "some accused arrested",
    "remaining accused",
    "others absconding",
    "another accused absconding",
    "hunt continues",
    "search for remaining accused",

    # English
    "one arrested",
    "two arrested",

    # Odia
    "ଜଣେ ଗିରଫ",
    "ଦୁଇଜଣ ଗିରଫ",
    "କେତେକ ଗିରଫ",
    "ଅନ୍ୟ ଫେରାର",
    "ଅବଶିଷ୍ଟ ଅଭିଯୁକ୍ତ"

]

def detect_case_status(text):

    text = text.lower()

    # Highest priority
    for keyword in PARTIALLY_SOLVED_KEYWORDS:
        if keyword.lower() in text:
            return "PARTIALLY_SOLVED"

    for keyword in SOLVED_KEYWORDS:
        if keyword.lower() in text:
            return "SOLVED"

    for keyword in ONGOING_KEYWORDS:
        if keyword.lower() in text:
            return "ONGOING"

    for keyword in UNSOLVED_KEYWORDS:
        if keyword.lower() in text:
            return "UNSOLVED"

    return "UNKNOWN"
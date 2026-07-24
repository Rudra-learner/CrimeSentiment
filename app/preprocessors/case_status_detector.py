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
    "police custody",
    "accused arrested",
    "all accused arrested",
    "gang arrested",
    "mastermind arrested",
    "kingpin arrested",

    # Seizure / Recovery
    "recovered",
    "property recovered",
    "weapon recovered",
    "loot recovered",
    "cash recovered",
    "gold recovered",
    "bike recovered",
    "vehicle recovered",
    "mobile recovered",
    "seized",
    "items seized",
    "articles seized",

    # Chargesheet
    "chargesheet",
    "charge sheet",
    "charge-sheet",
    "chargesheet filed",
    "chargesheet submitted",
    "final report filed",

    # Court
    "convicted",
    "found guilty",
    "sentenced",
    "life imprisonment",
    "death sentence",
    "rigorous imprisonment",
    "fine imposed",
    "court convicted",
    "court sentenced",
    "judgement",
    "judgment",
    "verdict",

    # Police Success
    "case solved",
    "crime solved",
    "crime cracked",
    "case cracked",
    "mystery solved",
    "gang busted",

    # Cyber
    "money recovered",
    "account frozen",
    "refund issued",

    # Odia
    "ଗିରଫ",
    "ଗିରଫତାର",
    "ଧରାପଡିଲେ",
    "ଚାର୍ଜସିଟ",
    "ଦଣ୍ଡିତ",
    "ଜେଲ",
    "ଦୋଷୀ",
    "ଜବତ",
    "ଉଦ୍ଧାର"
]

ONGOING_KEYWORDS = [

    # Investigation
    "investigation",
    "under investigation",
    "probe",
    "investigating",
    "further investigation",
    "crime branch investigating",

    # FIR
    "fir",
    "fir registered",
    "case registered",
    "registered a case",
    "complaint lodged",
    "complaint filed",
    "complaint received",

    # Inquiry
    "inquiry",
    "enquiry",
    "departmental inquiry",
    "internal inquiry",
    "disciplinary inquiry",

    # Suspension
    "suspended",
    "suspension",
    "placed under suspension",

    # Police action
    "questioning",
    "interrogation",
    "search operation",
    "collecting evidence",
    "recording statement",
    "cctv footage",
    "forensic examination",
    "forensic team",
    "awaiting report",
    "post mortem report",
    "viscera report",
    "pending investigation",
    "pending inquiry",

    # Vigilance
    "vigilance",
    "departmental proceedings",

    # Odia
    "ତଦନ୍ତ",
    "ଯାଞ୍ଚ",
    "ଅନୁସନ୍ଧାନ",
    "ପଚରାଉଚରା",
    "ମାମଲା ରୁଜୁ",
    "ଏଫଆଇଆର",
    "ଅଭିଯୋଗ"

]

UNSOLVED_KEYWORDS = [

    "unknown accused",
    "unknown persons",
    "unknown criminals",
    "unknown miscreants",

    "identity unknown",
    "unidentified",

    "absconding",
    "on the run",
    "escaped",
    "suspect fled",

    "not arrested",
    "yet to be arrested",
    "yet to be traced",

    "search continues",

    "still missing",
    "missing",
    "not traced",

    "body yet to be identified",

    "no clue",
    "no breakthrough",

    "ଅଜଣା",
    "ଅଜ୍ଞାତ",
    "ଫେରାର",
    "ନିଖୋଜ",
    "ଧରାପଡିନାହିଁ"

]

PARTIALLY_SOLVED_KEYWORDS = [

    "one accused arrested",
    "two accused arrested",
    "three accused arrested",
    "four accused arrested",

    "some accused arrested",
    "few accused arrested",

    "remaining accused",
    "remaining accused absconding",
    "others absconding",

    "hunt continues",
    "search for remaining accused",

    "one arrested while others absconding",
    "main accused absconding",

    "one arrested",
    "two arrested",

    "ଜଣେ ଗିରଫ",
    "ଦୁଇଜଣ ଗିରଫ",
    "ଅନ୍ୟ ଫେରାର",
    "ଅବଶିଷ୍ଟ ଅଭିଯୁକ୍ତ"

]

def detect_case_status(text):

    text = text.lower().strip()

    # Highest priority
    for keyword in PARTIALLY_SOLVED_KEYWORDS:
        if keyword.lower() in text:
            return "PARTIALLY_SOLVED"

    # Solved
    for keyword in SOLVED_KEYWORDS:
        if keyword.lower() in text:
            return "SOLVED"

    # Unsolved
    for keyword in UNSOLVED_KEYWORDS:
        if keyword.lower() in text:
            return "UNSOLVED"

    # Ongoing
    for keyword in ONGOING_KEYWORDS:
        if keyword.lower() in text:
            return "ONGOING"

    return "UNKNOWN"
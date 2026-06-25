SOLVED_KEYWORDS = [

    "arrested",
    "held",
    "apprehended",
    "detained",
    "taken into custody",
    "nabbed",
    "caught",
    "captured",
    "case solved",
    "solved",
    "cracked",
    "identified",
    "chargesheet filed",
    "charge sheet filed",
    "convicted",
    "sentenced",
    "accused arrested",
    "all accused arrested",
    "police solved",
    "crime solved"

]


ONGOING_KEYWORDS = [

    "investigation",
    "investigation underway",
    "probe",
    "probe underway",
    "police investigating",
    "under investigation",
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
    "suspected",
    "further investigation",
    "crime branch investigating"

]


UNSOLVED_KEYWORDS = [

    "unknown accused",
    "unidentified",
    "absconding",
    "on the run",
    "missing",
    "yet to be traced",
    "no clue",
    "no breakthrough",
    "could not trace",
    "could not identify",
    "still missing",
    "search continues",
    "accused escaped",
    "fled",
    "escaped",
    "not arrested"

]


PARTIALLY_SOLVED_KEYWORDS = [

    "one accused arrested",
    "two accused arrested",
    "some accused arrested",
    "others absconding",
    "remaining accused",
    "hunt continues",
    "search for remaining accused",
    "another accused absconding"

]


def detect_case_status(text):

    text = text.lower()

    for keyword in PARTIALLY_SOLVED_KEYWORDS:

        if keyword in text:
            return "PARTIALLY_SOLVED"

    for keyword in SOLVED_KEYWORDS:

        if keyword in text:
            return "SOLVED"

    for keyword in ONGOING_KEYWORDS:

        if keyword in text:
            return "ONGOING"

    for keyword in UNSOLVED_KEYWORDS:

        if keyword in text:
            return "UNSOLVED"

    return "UNKNOWN"
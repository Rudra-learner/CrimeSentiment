from ast import pattern
from pydoc import doc, text
import re
import token

import spacy

from app.database.database import SessionLocal
from app.models.officer_mention import OfficerMention
from app.models.article import RawArticle
from app.models.processed_article import ProcessedArticle
from app.models.news_event import NewsEvent
from app.models.analysis_result import AnalysisResult


nlp = spacy.load("en_core_web_sm")


ENGLISH_DESIGNATIONS = [
    "DGP",
    "ADG",
    "IG",
    "DIG",
    "SP",
    "Additional SP",
    "ASP",
    "DSP",
    "SDPO",
    "Inspector",
    "Inspector-in-Charge",
    "Inspector In Charge",
    "IIC",
    "SHO",
    "OC",
    "SI",
    "Sub Inspector",
    "ASI",
    "Assistant Sub Inspector",
    "Head Constable",
    "Constable"
]


ODIA_DESIGNATIONS = [
    "ଡିଜିପି",
    "ଏସପି",
    "ଅତିରିକ୍ତ ଏସପି",
    "ଡିଏସପି",
    "ଏସଆଇ",
    "ଏଏସଆଇ",
    "ଆଇଆଇସି",
    "ଇନ୍ସପେକ୍ଟର",
    "କନଷ୍ଟେବଳ"
]


ORGANIZATIONS = [
    "Odisha Police",
    "Nayagarh Police",
    "Crime Branch",
    "CID",
    "STF",
    "Special Task Force",
    "ଓଡ଼ିଶା ପୁଲିସ",
    "ନୟାଗଡ଼ ପୁଲିସ",
    "କ୍ରାଇମ ବ୍ରାଞ୍ଚ",
    "ସିଆଇଡି",
    "ଏସଟିଏଫ"
]


INVALID_PERSONS = {
    "Police",
    "Officer",
    "Crime",
    "Branch",
    "CID",
    "STF",
    "Odisha",
    "Nayagarh",
    "Government",
    "Court",
    "Judge",
    "General"
}

INVALID_VIPS = {

    "Mohan Charan Majhi",
    "Naveen Patnaik",
    "Narendra Modi",
    "Amit Shah",
    "Droupadi Murmu",
    "Dharmendra Pradhan",
    "Prithviraj Harichandan"

}

INVALID_TITLES = [

    "Chief Minister",
    "CM",
    "Prime Minister",
    "PM",
    "Governor",
    "Minister",
    "Cabinet",
    "MLA",
    "MP",
    "Mayor",
    "Collector",
    "Commissioner"

]

POLICE_CONTEXT = [

    "police",
    "investigation",
    "crime branch",
    "station",
    "raid",
    "iic",
    "sp",
    "si",
    "asi",
    "inspector",
    "constable",
    "officer",
    "arrest"

]

def contains_odia(text):
    return bool(re.search(r"[\u0B00-\u0B7F]", text))


def normalize_name(name):
    name = " ".join(name.split())
    name = name.replace(".", "")
    return name.strip().title()


class EntityExtractor:

    def __init__(self):
        self.db = SessionLocal()

    def extract_entities(self, text):
        if contains_odia(text):
            return {
                "persons": [],
                "locations": [],
                "organizations": self.extract_police_organizations(text)
            }

        doc = nlp(text[:3000])

        persons = []
        locations = []
        organizations = []

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                person = normalize_name(ent.text)
                if person not in INVALID_PERSONS:
                    persons.append(person)
            elif ent.label_ in ["GPE", "LOC"]:
                locations.append(ent.text.strip())
            elif ent.label_ == "ORG":
                organizations.append(ent.text.strip())

        return {
            "persons": sorted(list(set(persons))),
            "locations": sorted(list(set(locations))),
            "organizations": sorted(
                list(set(organizations + self.extract_police_organizations(text)))
            )
        }

    def extract_officers(self, text):

        officers = []

        if not contains_odia(text):

            for designation in ENGLISH_DESIGNATIONS:

                pattern = rf"\b{re.escape(designation)}\b\s+([A-Z][a-zA-Z\.]+(?:\s+[A-Z][a-zA-Z\.]+){{1,3}})"

                matches = re.findall(pattern, text)

                for match in matches:

                    name = normalize_name(match)

                    if name in INVALID_PERSONS:
                        continue

                    if len(name.split()) < 2:
                        continue

                    officer = {
                        "designation": designation,
                        "name": name
                    }

                    if officer not in officers:
                        officers.append(officer)

            return officers

        for designation in ODIA_DESIGNATIONS:

            pattern = rf"{designation}\s+([\u0B00-\u0B7F]+(?:\s+[\u0B00-\u0B7F]+){{1,3}})"

            matches = re.findall(pattern, text)

            for match in matches:

                name = " ".join(match.split())

                officer = {
                    "designation": designation,
                    "name": name
                }

                if officer not in officers:
                    officers.append(officer)

        return officers

    def extract_police_stations(self, text):

        police_stations = []

        patterns = [
            r"([A-Z][A-Za-z ]+ Police Station)",
            r"([A-Z][A-Za-z ]+ PS)",
            r"([A-Z][A-Za-z ]+ Police Outpost)",
            r"([\u0B00-\u0B7F ]+ଥାନା)"
        ]

        for pattern in patterns:

            matches = re.findall(pattern, text)

            for station in matches:

                station = station.strip()

                if len(station.split()) > 5:
                    continue

                if station not in police_stations:
                    police_stations.append(station)

        return police_stations

    def extract_police_organizations(self, text):
        detected = []
        text_lower = text.lower()

        for org in ORGANIZATIONS:
            if org.lower() in text_lower:
                detected.append(org)

        return sorted(list(set(detected)))

    def combine_entities(self, text):
        basic_entities = self.extract_entities(text)
        officers = self.extract_officers(text)
        police_stations = self.extract_police_stations(text)
        police_orgs = self.extract_police_organizations(text)

        return {
            "officers": officers,
            "persons": sorted(list(set(basic_entities["persons"]))),
            "locations": sorted(list(set(basic_entities["locations"]))),
            "organizations": sorted(
                list(set(basic_entities["organizations"] + police_orgs))
            ),
            "police_stations": sorted(list(set(police_stations)))
        }

    def save_officer_mentions(self, processed_article_id, entities):
        officers = entities["officers"]
        police_stations = entities["police_stations"]

        station = None

        if police_stations:
            station = police_stations[0]

        for officer in officers:
            name = officer["name"].strip()
            designation = officer["designation"]

            if len(name) < 3:
                continue

            if len(name.split()) > 4:
                continue

            exists = (
                self.db.query(OfficerMention)
                .filter(
                    OfficerMention.processed_article_id == processed_article_id,
                    OfficerMention.officer_name == name,
                    OfficerMention.designation == designation
                )
                .first()
            )

            if exists:
                continue

            mention = OfficerMention(
                processed_article_id=processed_article_id,
                officer_name=name,
                designation=designation,
                police_station=station
            )

            self.db.add(mention)

        self.db.commit()

    def process_article(self, article):
        print(f"\nExtracting Entities : {article.title}")

        entities = self.combine_entities(article.clean_text)

        print(f"Officers : {entities['officers']}")
        print(f"Stations : {entities['police_stations']}")

        self.save_officer_mentions(article.id, entities)

        return entities

    def process_all_articles(self):
        articles = self.db.query(ProcessedArticle).all()

        print(f"\nFound {len(articles)} articles.\n")

        for article in articles:
            try:
                self.process_article(article)
            except Exception as e:
                print(f"Entity Extraction Error : {e}")
                self.db.rollback()

        print("\nEntity Extraction Completed.\n")

    def close(self):
        self.db.close()


def run_entity_extractor():
    extractor = EntityExtractor()

    try:
        extractor.process_all_articles()
    finally:
        extractor.close()


if __name__ == "__main__":
    run_entity_extractor()
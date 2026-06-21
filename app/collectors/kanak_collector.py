import requests
import re
import time

from bs4 import BeautifulSoup
from datetime import datetime
from langdetect import detect

from app.database.database import SessionLocal
from app.models.article import RawArticle


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_SEARCH_URL = "https://kanaknews.com/search?title="

SEARCH_TERMS = [

    "ନୟାଗଡ଼",
    "ରଣପୁର",
    "ଦଶପଲ୍ଲା",
    "ଓଡ଼ଗାଁ",
    "ଖଣ୍ଡପଡା",
    "ଗଣିଆ",
    "ଭାପୁର",
    "ଫତେଗଡ଼",

    "ନୟାଗଡ଼ ପୋଲିସ",

    "ନୂଆଗାଁ",
    "ସରାଙ୍କୁଳ",
    "କଣ୍ଟିଲୋ",
    "ଇଟାମାଟି",
    "ରାଜସୁନାଖଳା",

    "ହତ୍ୟା",
    "ଚୋରି",
    "ଡକାୟତି",
    "ଗିରଫ",
    "ଅପରାଧ",
    "ହତ୍ୟାକାଣ୍ଡ",
    "ଲୁଟ",
    "ବ୍ରାଉନସୁଗାର",
    "ଗଞ୍ଜେଇ",
    "ସାଇବର ଠକେଇ"

]


NAYAGARH_KEYWORDS = [

    "nayagarh",
    "ନୟାଗଡ଼",

    "ranpur",
    "ରଣପୁର",

    "daspalla",
    "ଦଶପଲ୍ଲା",

    "odagaon",
    "ଓଡ଼ଗାଁ",

    "khandapada",
    "ଖଣ୍ଡପଡା",

    "gania",
    "ଗଣିଆ",

    "bhapur",
    "ଭାପୁର",

    "fategarh",
    "ଫତେଗଡ଼",

    "nayagarh police",
    "ନୟାଗଡ଼ ପୋଲିସ"
]


def article_exists(db, url):

    return (
        db.query(RawArticle)
        .filter(RawArticle.url == url)
        .first()
        is not None
    )


def is_nayagarh_related(title, article_text):

    text = (
        (title or "") +
        " " +
        (article_text or "")
    ).lower()

    for keyword in NAYAGARH_KEYWORDS:

        if keyword.lower() in text:
            return True

    return False


def save_article(
    db,
    title,
    source,
    url,
    language,
    article_text
):

    if article_exists(db, url):

        print("Already Exists:", url)
        return False

    article = RawArticle(

        title=title,
        source=source,
        url=url,

        language=language,
        published_date="",

        article_text=article_text,

        collected_at=datetime.utcnow()

    )

    db.add(article)
    db.commit()

    print("Saved:", title)

    return True


def extract_article(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = ""

        h1 = soup.find("h1")

        if h1:

            title = h1.get_text(
                strip=True
            )

        elif soup.title:

            title = soup.title.get_text(
                strip=True
            )

        article_text = ""

        selectors = [

            "article",
            '[class*="content"]',
            '[class*="story"]',
            '[class*="article"]',
            '[class*="detail"]',
            '[class*="news"]'

        ]

        for selector in selectors:

            for tag in soup.select(selector):

                text = tag.get_text(
                    separator=" ",
                    strip=True
                )

                if len(text) > len(article_text):
                    article_text = text

        footer_markers = [

            "by Kanak Digital Desk",
            "Link copied!",
            "Copy failed!",
            "Follow us:",
            "Powered by",
            "Subscribe to our Newsletter!",
            "Join and get latest news updates delivered to you via social media"
        ]

        for marker in footer_markers:

            if marker in article_text:

                article_text = article_text.split(
                    marker
                )[0]

        article_text = article_text.replace(
            "Advertisment",
            ""
        )

        article_text = article_text.replace(
            "Crime Photograph: (Kanak News)",
            ""
        )

        article_text = re.sub(
            r"\s+",
            " ",
            article_text
        ).strip()

        if len(article_text) < 200:
            return None

        try:
            language = detect(article_text)

        except:
            language = "unknown"

        return {

            "title": title,
            "url": url,
            "language": language,
            "article_text": article_text

        }

    except Exception as e:

        print("Extraction Error:", e)
        return None


def collect_urls(search_term):

    urls = set()

    try:

        search_url = (
            BASE_SEARCH_URL +
            search_term.replace(" ", "+")
        )

        print("Search URL:", search_url)

        response = requests.get(
            search_url,
            headers=HEADERS,
            timeout=20
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if (
                "kanaknews.com" in href
                and "/news/" in href
            ):
                urls.add(href)

    except Exception as e:

        print("Search Error:", e)

    return list(urls)


def main():

    db = SessionLocal()

    try:

        total_saved = 0

        for term in SEARCH_TERMS:

            print("\nSearching:", term)

            urls = collect_urls(term)

            print("Found", len(urls), "URLs")

            for url in urls:

                article = extract_article(url)

                if not article:
                    continue

                if not is_nayagarh_related(

                    article["title"],
                    article["article_text"]

                ):

                    print(
                        "Skipped Non-Nayagarh:",
                        article["title"]
                    )

                    continue

                saved = save_article(

                    db=db,

                    title=article["title"],

                    source="Kanak News",

                    url=article["url"],

                    language=article["language"],

                    article_text=article["article_text"]

                )

                if saved:
                    total_saved += 1

                time.sleep(1)

        print("\nTotal Saved:", total_saved)

    finally:

        db.close()


if __name__ == "__main__":
    main()
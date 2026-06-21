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

BASE_URLS = [

    "https://www.orissapost.com/state-news/",
    "https://www.orissapost.com/metro-news/",
    "https://www.orissapost.com/trending/"

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

    "nuagaon",
    "ନୂଆଗାଁ",

    "sarankul",
    "ସରଣକୁଳ",

    "kantilo",
    "କଣ୍ଟିଲୋ",

    "banigochha",
    "ବାଣିଗୋଛା",

    "nayagarh police",
    "ନୟାଗଡ଼ ପୋଲିସ",

    "nayagarh murder",
    "nayagarh theft",
    "nayagarh robbery",
    "nayagarh crime",
    "nayagarh arrest"

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


def is_article_url(url):

    if not url.startswith(
        "https://www.orissapost.com/"
    ):
        return False

    blocked_words = [

        "facebook",
        "twitter",
        "linkedin",
        "youtube",
        "pinterest",
        "whatsapp",

        "/category/",
        "/tag/",
        "/author/",

        "/about-us/",
        "/advertise/",
        "/contact-us/",
        "/jobs/",

        "/state-news/",
        "/metro-news/",
        "/sports-news/",
        "/business-news/",
        "/editorial/",
        "/opinion/",
        "/feature/",
        "/horoscope/",
        "/timeout/",
        "/careers/",
        "/sci-tech/",
        "/trending/",
        "/todays-pic/",
        "/photo-news/",
        "/india-national-news/",
        "/international-news/",
        "/entertainment-news/",
        "/odisha-special/",

        "#comments"

    ]

    for word in blocked_words:

        if word in url:
            return False

    if url.endswith(
        (
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp"
        )
    ):
        return False

    path = url.replace(
        "https://www.orissapost.com/",
        ""
    ).strip("/")

    if len(path) < 10:
        return False

    if len(path.split("/")) > 1:
        return False

    return True


def collect_urls():

    urls = set()

    for page_url in BASE_URLS:

        try:

            print("\nScanning:", page_url)

            response = requests.get(
                page_url,
                headers=HEADERS,
                timeout=20
            )

            print(
                "Status:",
                response.status_code
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            links = soup.find_all(
                "a",
                href=True
            )

            print(
                "Links Found:",
                len(links)
            )

            for a in links:

                href = a["href"].strip()

                if is_article_url(href):

                    urls.add(href)

        except Exception as e:

            print(
                "Collection Error:",
                e
            )

    return list(urls)


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
            '[class*="post"]',
            '[class*="entry"]',
            '[class*="article"]',
            '[class*="story"]'

        ]

        for selector in selectors:

            for tag in soup.select(
                selector
            ):

                text = tag.get_text(
                    separator=" ",
                    strip=True
                )

                if len(text) > len(article_text):

                    article_text = text

        article_text = re.sub(
            r"\s+",
            " ",
            article_text
        ).strip()

        if len(article_text) < 200:

            return None

        try:

            language = detect(
                article_text
            )

        except:

            language = "unknown"

        return {

            "title": title,
            "url": url,
            "language": language,
            "article_text": article_text

        }

    except Exception as e:

        print(
            "Extraction Error:",
            e
        )

        return None


def main():

    db = SessionLocal()

    try:

        urls = collect_urls()

        print(
            "\nTotal URLs Found:",
            len(urls)
        )

        total_saved = 0

        for url in urls:

            article = extract_article(
                url
            )

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

                source="Orissa Post",

                url=article["url"],

                language=article["language"],

                article_text=article["article_text"]

            )

            if saved:

                total_saved += 1

            time.sleep(1)

        print(
            "\nTotal Saved:",
            total_saved
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()
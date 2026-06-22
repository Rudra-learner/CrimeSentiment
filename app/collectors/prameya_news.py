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

    "https://www.prameyanews.com/category/odisha",
    "https://www.prameyanews.com/category/crime"

]


NAYAGARH_KEYWORDS = [

    "nayagarh",
    "ranpur",
    "daspalla",
    "odagaon",
    "khandapada",
    "gania",
    "bhapur",
    "fategarh",

    "nuagaon",
    "sarankul",
    "kantilo",
    "itamati",
    "banigochha",
    "rajasunakhala",

    "nayagarh police"
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
        "https://www.prameyanews.com/"
    ):
        return False

    blocked = [

        "/category/",
        "/tag/",

        "facebook",
        "instagram",
        "youtube",
        "twitter",
        "x.com",
        "whatsapp",

        "privacy-policy",
        "contact-us",

        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]

    for word in blocked:

        if word in url:
            return False

    path = url.replace(
        "https://www.prameyanews.com/",
        ""
    ).strip("/")

    if len(path) < 15:
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

        if soup.title:

            title = (
                soup.title.get_text(
                    strip=True
                )
                .replace(
                    " - Prameya News",
                    ""
                )
                .strip()
            )

        article_text = ""

        content = soup.find(
            "div",
            class_="post-description"
        )

        if content:

            article_text = content.get_text(
                separator=" ",
                strip=True
            )

        else:

            selectors = [

                ".post-description",

                '[class*="description"]',
                '[class*="content"]',
                '[class*="article"]',
                '[class*="story"]',
                '[class*="post"]'

            ]

            for selector in selectors:

                tag = soup.select_one(
                    selector
                )

                if tag:

                    article_text = tag.get_text(
                        separator=" ",
                        strip=True
                    )

                    if len(article_text) > 200:
                        break

        article_text = re.sub(
            r"\s+",
            " ",
            article_text
        ).strip()

        if len(article_text) < 100:

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

                source="Prameya News",

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
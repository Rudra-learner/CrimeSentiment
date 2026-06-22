import requests
import feedparser
import re
import time

from bs4 import BeautifulSoup
from datetime import datetime
from langdetect import detect

from app.database.database import SessionLocal
from app.models.article import RawArticle


RSS_URL = "https://www.orissapost.com/feed/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def article_exists(db, url):

    return (
        db.query(RawArticle)
        .filter(RawArticle.url == url)
        .first()
        is not None
    )


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
            timeout=30
        )

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = ""

        if soup.title:
            title = soup.title.get_text(
                strip=True
            )

        article_text = ""

        selectors = [

            ".entry-content",
            ".post-content",
            ".td-post-content",
            ".article-content",

            "article",
            '[class*="content"]',
            '[class*="post"]',
            '[class*="entry"]',
            '[class*="article"]'

        ]

        for selector in selectors:

            try:

                for tag in soup.select(selector):

                    text = tag.get_text(
                        separator=" ",
                        strip=True
                    )

                    if len(text) > len(article_text):

                        article_text = text

            except:
                pass

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


def collect_urls():

    urls = []

    try:

        print(
            "Reading RSS Feed..."
        )

        feed = feedparser.parse(
            RSS_URL
        )

        print(
            "Articles Found:",
            len(feed.entries)
        )

        for entry in feed.entries:

            if hasattr(
                entry,
                "link"
            ):

                urls.append(
                    entry.link
                )

    except Exception as e:

        print(
            "RSS Error:",
            e
        )

    return urls


def main():

    db = SessionLocal()

    try:

        urls = collect_urls()

        print(
            "\nTotal URLs:",
            len(urls)
        )

        total_saved = 0

        for url in urls:

            article = extract_article(
                url
            )

            if not article:
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
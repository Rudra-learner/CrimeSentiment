import requests
from bs4 import BeautifulSoup
from newspaper import Article
from datetime import datetime

from app.database.database import SessionLocal
from app.models.article import RawArticle


SEARCH_TERMS = [
    "nayagarh murder",
    "nayagarh crime",
    "nayagarh police",
    "nayagarh theft",
    "nayagarh robbery",
    "nayagarh cyber fraud",
    "nayagarh arrest",
    "nayagarh rape",
    "nayagarh missing",
    "nayagarh accident"
]

BASE_SEARCH_URL = "https://pragativadi.com/?s="

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def normalize_url(url):

    if not url:
        return None

    url = url.split("#")[0]

    if url.endswith("/"):
        url = url[:-1]

    return url


def article_exists(db, url):

    return db.query(RawArticle).filter(
        RawArticle.url == url
    ).first()


def save_article(
    db,
    title,
    source,
    url,
    language,
    published_date,
    article_text
):

    if article_exists(db, url):
        return

    article = RawArticle(
        title=title,
        source=source,
        url=url,
        language=language,
        published_date=published_date,
        article_text=article_text,
        collected_at=datetime.utcnow(),
        is_preprocessed=False
    )

    db.add(article)
    db.commit()

    print(f"Saved: {title}")


def extract_article(article_url):

    try:

        article = Article(article_url)

        article.download()
        article.parse()

        title = article.title
        text = article.text

        if len(text.strip()) < 100:
            return None, None

        return title, text

    except Exception as e:

        print(f"Article Extraction Error: {e}")

        try:

            response = requests.get(
                article_url,
                headers=HEADERS,
                timeout=10
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            title = ""

            if soup.title:
                title = soup.title.get_text(strip=True)

            paragraphs = soup.find_all("p")

            text = " ".join(
                p.get_text(" ", strip=True)
                for p in paragraphs
            )

            if len(text.strip()) < 100:
                return None, None

            return title, text

        except Exception as e2:

            print(
                f"Fallback Extraction Error: {e2}"
            )

            return None, None


def collect_articles():

    print("\nCollecting Pragativadi Articles...\n")

    db = SessionLocal()

    saved_count = 0

    try:

        for keyword in SEARCH_TERMS:

            print(f"\nSearching: {keyword}")

            search_url = (
                BASE_SEARCH_URL +
                keyword.replace(" ", "+")
            )

            response = requests.get(
                search_url,
                headers=HEADERS,
                timeout=20
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            links = soup.find_all("a")

            for link in links:

                href = link.get("href")

                if not href:
                    continue

                href = normalize_url(href)

                if not href:
                    continue

                if "#respond" in href:
                    continue

                if "pragativadi.com" not in href:
                    continue

                if "/category/" in href:
                    continue

                if article_exists(db, href):
                    continue

                title, article_text = extract_article(
                    href
                )

                if not title:
                    continue

                combined_text = (
                    title.lower() +
                    " " +
                    article_text.lower()
                )

                if "nayagarh" not in combined_text:
                    continue

                save_article(
                    db=db,
                    title=title,
                    source="Pragativadi",
                    url=href,
                    language="en",
                    published_date=str(
                        datetime.utcnow()
                    ),
                    article_text=article_text
                )

                saved_count += 1

        print(
            f"\nTotal Articles Saved: {saved_count}"
        )

    except Exception as e:

        print(f"Collector Error: {e}")

    finally:

        db.close()


if __name__ == "__main__":
    collect_articles()
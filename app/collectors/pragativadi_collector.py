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

        collected_at=datetime.utcnow()

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

        return title, text

    except Exception as e:

        print("Article Extraction Error:", e)

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

                headers={
                    "User-Agent": "Mozilla/5.0"
                },

                timeout=20
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            links = soup.find_all("a")

            for link in links:

                href = link.get("href")

                title_text = link.get_text(
                    strip=True
                )

                if not href:
                    continue

                if not title_text:
                    continue

                if "pragativadi.com" not in href:
                    continue

                if "/category/" in href:
                    continue

                if article_exists(db, href):
                    continue

                try:

                    title, article_text = extract_article(
                        href
                    )

                    if not title:
                        continue

                    title_lower = title.lower()

                    if "nayagarh" not in title_lower:
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

                except Exception as e:

                    print("Save Error:", e)

        print(
            f"\nTotal Articles Saved: {saved_count}"
        )

    except Exception as e:

        print("Collector Error:", e)

    finally:

        db.close()


if __name__ == "__main__":

    collect_articles()
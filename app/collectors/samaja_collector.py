from datetime import datetime
import requests

from bs4 import BeautifulSoup
from newspaper import Article
from langdetect import detect

from app.database.database import SessionLocal
from app.models.article import RawArticle


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_URL = "https://thesamaja.live/category/odisha/"




def article_exists(db, url):
    return (
        db.query(RawArticle)
        .filter(RawArticle.url == url)
        .first()
        is not None
    )


def extract_article(url):
    try:
        print(f"\nDownloading: {url}")
        news = Article(
            url,
            language="or"  # Using Odia language hint
        )
        news.download()
        news.parse()

        title = news.title.strip()
        article_text = news.text.strip()
        published_date = ""

        if news.publish_date:
            published_date = str(news.publish_date)

        if not published_date:
            try:
                res = requests.get(url, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                for time_tag in soup.find_all("time"):
                    text = time_tag.get_text(strip=True)
                    if text:
                        published_date = text
                        break
            except:
                pass

        try:
            language = detect(article_text)
        except:
            language = "unknown"

        return {
            "title": title,
            "article_text": article_text,
            "published_date": published_date,
            "language": language
        }

    except Exception as e:
        print(f"Article Error: {e}")
        return None





def save_article(db, title, url, article_text, published_date, language):
    try:
        article = RawArticle(
            title=title,
            source="The Samaja",
            url=url,
            language=language,
            published_date=published_date,
            article_text=article_text,
            collected_at=datetime.utcnow()
        )
        db.add(article)
        db.commit()
        print(f"Saved: {title}")
        return True
    except Exception as e:
        db.rollback()
        print(f"Database Error: {e}")
        return False


def collect_article_urls():
    article_urls = set()
    try:
        for page in range(1, 6):  # The Samaja pages
            page_url = f"{BASE_URL}page/{page}/" if page > 1 else BASE_URL
            print(f"\nProcessing Page {page}")

            response = requests.get(page_url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("https://thesamaja.live/") and "category" not in href and "tag" not in href:
                    article_urls.add(href)
    except Exception as e:
        print(f"URL Collection Error: {e}")

    return article_urls


def collect_articles():
    print("\n================================")
    print("THE SAMAJA NAYAGARH COLLECTOR")
    print("================================\n")

    db = SessionLocal()
    saved_count = 0

    try:
        urls = collect_article_urls()
        print(f"\nTotal URLs Found: {len(urls)}")

        for url in urls:
            if article_exists(db, url):
                print("Already Exists")
                continue

            article = extract_article(url)
            if not article:
                continue

            print("\nTITLE:")
            print(article["title"])
            print("\nDATE:")
            print(article["published_date"])
            print("\nLANGUAGE:")
            print(article["language"])
            print("\nTEXT LENGTH:")
            print(len(article["article_text"]))

            saved = save_article(
                db=db,
                title=article["title"],
                url=url,
                article_text=article["article_text"],
                published_date=article["published_date"],
                language=article["language"]
            )
            if saved:
                saved_count += 1

        print("\n========================")
        print(f"TOTAL SAVED: {saved_count}")
        print("========================")

    finally:
        db.close()

if __name__ == "__main__":
    collect_articles()

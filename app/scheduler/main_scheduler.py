import time

from app.collectors.odisha_tv_collector import collect_articles as odisha_tv
from app.collectors.orissa_post import main as orissa_post
from app.collectors.kanak_collector import main as kanak_news
from app.collectors.pragativadi_collector import collect_articles as pragativadi
from app.collectors.prameya_news import main as prameya

# New Collectors
from app.collectors.ndtv_collector import collect_articles as ndtv_news
from app.collectors.samaja_collector import collect_articles as samaja_news
from app.collectors.toi_collector import collect_articles as toi_news
from app.collectors.dharitri_collector import collect_articles as dharitri_news
from app.collectors.odisha_bhaskar_collector import collect_articles as odisha_bhaskar_news
from app.collectors.prajatantra_collector import collect_articles as prajatantra_news
from app.collectors.kalinga_tv_collector import collect_articles as kalinga_tv_news
from app.collectors.argus_news_collector import collect_articles as argus_news
from app.collectors.naxatra_news_collector import collect_articles as naxatra_news
from app.collectors.hindu_collector import collect_articles as hindu_news
from app.collectors.ht_collector import collect_articles as ht_news
from app.collectors.indian_express_collector import collect_articles as indian_express_news

from app.preprocessors.preprocessor import preprocess_articles


def run_pipeline():
    print("\n================================")
    print("Starting Collection Pipeline")
    print("================================\n")

    collectors = [
        ("Orissa Post", orissa_post),
        ("Kanak News", kanak_news),
        ("Pragativadi", pragativadi),
        ("Prameya", prameya),
        ("Odisha TV", odisha_tv),
        ("NDTV", ndtv_news),
        ("The Samaja", samaja_news),
        ("Times of India", toi_news),
        ("Dharitri", dharitri_news),
        ("Odisha Bhaskar", odisha_bhaskar_news),
        ("Prajatantra", prajatantra_news),
        ("Kalinga TV", kalinga_tv_news),
        ("Argus News", argus_news),
        ("Naxatra News", naxatra_news),
        ("The Hindu", hindu_news),
        ("Hindustan Times", ht_news),
        ("The Indian Express", indian_express_news),
    ]

    for name, func in collectors:
        try:
            print(f"Running {name} Collector...")
            func()
        except Exception as e:
            print(f"{name} Error: {e}")

    print("\n================================")
    print("Collection Completed")
    print("================================\n")

    try:
        print("\n================================")
        print("Starting Preprocessing")
        print("================================\n")
        preprocess_articles()
        print("\n================================")
        print("Preprocessing Completed")
        print("================================\n")
    except Exception as e:
        print("Preprocessor Error:", e)

    print("\n================================")
    print("Pipeline Completed Successfully")
    print("================================\n")


if __name__ == "__main__":
    import schedule
    # Run every 30 minutes
    schedule.every(30).minutes.do(run_pipeline)
    
    # Run once immediately when scheduler starts
    run_pipeline()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            print("Scheduler Error:", e)
            time.sleep(60)
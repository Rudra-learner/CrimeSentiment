import schedule
import time

from app.collectors.odisha_tv_collector import collect_articles as odisha_tv
from app.collectors.orissa_post import main as orissa_post
from app.collectors.kanak_collector import main as kanak_news
from app.collectors.pragativadi_collector import collect_articles as pragativadi
from app.collectors.prameya_news import main as prameya

from app.preprocessors.preprocessor import preprocess_articles


def run_pipeline():

    print("\n================================")
    print("Starting Collection Pipeline")
    print("================================\n")

    # -----------------------------
    # Collectors
    # -----------------------------

    try:
        print("Running Orissa Post Collector...")
        orissa_post()
    except Exception as e:
        print("Orissa Post Error:", e)

    try:
        print("Running Kanak Collector...")
        kanak_news()
    except Exception as e:
        print("Kanak Error:", e)

    try:
        print("Running Pragativadi Collector...")
        pragativadi()
    except Exception as e:
        print("Pragativadi Error:", e)

    try:
        print("Running Prameya Collector...")
        prameya()
    except Exception as e:
        print("Prameya Error:", e)

    try:
        print("Running Odisha TV Collector...")
        odisha_tv()
    except Exception as e:
        print("Odisha TV Error:", e)

    print("\n================================")
    print("Collection Completed")
    print("================================\n")

    # -----------------------------
    # Preprocessing
    # -----------------------------

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
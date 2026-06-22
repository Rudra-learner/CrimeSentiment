import schedule
import time

from app.collectors.odisha_tv_collector import collect_articles as odisha_tv
from app.collectors.orissa_post import main as orissa_post
from app.collectors.kanak_collector import main as kanak_news
from app.collectors.pragativadi_collector import collect_articles as pragativadi
from app.collectors.prameya_news import main as prameya



def run_collectors():

    print("\n================================")
    print("Starting Collection")
    print("================================\n")

    try:
        orissa_post()
    except Exception as e:
        print("Orissa Post Error:", e)

    try:
        kanak_news()
    except Exception as e:
        print("Kanak Error:", e)

    try:
        pragativadi()
    except Exception as e:
        print("Pragativadi Error:", e)

    try:
        prameya()
    except Exception as e:
        print("Prameya Error:", e)

    try:
        odisha_tv()
    except Exception as e:
        print("Odisha TV Error:", e)

    print("\n================================")
    print("Collection Complete")
    print("================================\n")


schedule.every(30).minutes.do(run_collectors)

run_collectors()

while True:

    try:

        schedule.run_pending()

        time.sleep(60)

    except Exception as e:

        print("Scheduler Error:", e)

        time.sleep(60)
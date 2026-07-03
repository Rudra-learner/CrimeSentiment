from collections import defaultdict

from app.database.database import SessionLocal

from app.models.article import RawArticle
from app.models.processed_article import ProcessedArticle
from app.models.news_event import NewsEvent
from app.models.analysis_result import AnalysisResult
from app.models.officer_mention import OfficerMention


class OfficerSentiment:

    def __init__(self):

        self.db = SessionLocal()

        self.officer_stats = defaultdict(
            lambda: {
                "Positive": 0,
                "Neutral": 0,
                "Negative": 0,
                "total_articles": 0,
                "confidence_sum": 0.0
            }
        )

    def fetch_officer_sentiments(self):

        results = (
            self.db.query(
                OfficerMention,
                AnalysisResult
            )
            .join(
                AnalysisResult,
                OfficerMention.processed_article_id ==
                AnalysisResult.processed_article_id
            )
            .all()
        )

        return results

    def calculate_statistics(self):

        records = self.fetch_officer_sentiments()

        print(f"\nFound {len(records)} officer mentions.\n")

        for mention, analysis in records:

            officer = mention.officer_name.strip()

            sentiment = analysis.sentiment

            confidence = analysis.confidence

            self.officer_stats[officer][sentiment] += 1

            self.officer_stats[officer]["total_articles"] += 1

            self.officer_stats[officer]["confidence_sum"] += confidence

        return self.officer_stats
    
    def determine_overall_sentiment(
        self,
        positive,
        neutral,
        negative
    ):

            if positive >= neutral and positive >= negative:
                return "Positive"

            elif neutral >= positive and neutral >= negative:
                return "Neutral"

            else:
                return "Negative"
            
    

    def generate_report(self):

        statistics = self.calculate_statistics()

        report = []

        for officer, data in statistics.items():

            if data["total_articles"] == 0:
                continue

            average_confidence = (
                data["confidence_sum"] /
                data["total_articles"]
            )

            overall_sentiment = self.determine_overall_sentiment(

    data["Positive"],

    data["Neutral"],

    data["Negative"]

)

            report.append({

                "officer_name": officer,

                "overall_sentiment": overall_sentiment,

                "positive": data["Positive"],

                "neutral": data["Neutral"],

                "negative": data["Negative"],

                "total_articles": data["total_articles"],

                "average_confidence": round(
                    average_confidence,
                    4
                )

            })

        report.sort(
            key=lambda x: x["total_articles"],
            reverse=True
        )

        return report

    def display_report(self):

        report = self.generate_report()

        print("\n")
        print("=" * 70)
        print("OFFICER SENTIMENT REPORT")
        print("=" * 70)

        if not report:

            print("\nNo Officer Sentiment Data Found.\n")
            return

        for officer in report:

            print(f"\nOfficer : {officer['officer_name']}")

            print(f"Overall Sentiment : {officer['overall_sentiment']}")

            print(f"Total Articles : {officer['total_articles']}")

            print(f"Positive : {officer['positive']}")

            print(f"Neutral : {officer['neutral']}")

            print(f"Negative : {officer['negative']}")

            print(
                f"Average Confidence : "
                f"{officer['average_confidence']:.2f}%"
            )

            print("-" * 70)

        print("\nOfficer Sentiment Analysis Completed.\n")

    def close(self):

        self.db.close()


def run_officer_sentiment():

    analyzer = OfficerSentiment()

    try:

        analyzer.display_report()

    finally:

        analyzer.close()


if __name__ == "__main__":

    run_officer_sentiment()
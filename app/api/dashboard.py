from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_, asc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.database.database import SessionLocal
from app.models.article import RawArticle
from app.models.processed_article import ProcessedArticle
from app.models.news_event import NewsEvent
from app.models.analysis_result import AnalysisResult
from app.models.officer_mention import OfficerMention

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_sentiment_score(sentiment_str):
    if sentiment_str and sentiment_str.lower() == 'positive': return 1
    if sentiment_str and sentiment_str.lower() == 'negative': return -1
    return 0

def apply_date_filter(query, model_col, days: int = None, start_date: str = None, end_date: str = None):
    if days:
        min_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(model_col >= min_date)
    elif start_date or end_date:
        try:
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(model_col >= start_dt)
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(model_col < end_dt)
        except ValueError:
            pass
    return query

@router.get("/kpi")
def get_kpi(db: Session = Depends(get_db), days: int = None, start_date: str = None, end_date: str = None, priority: str = None):
    total_raw = db.query(RawArticle).count()
    
    q_pa = db.query(ProcessedArticle)
    q_pa = apply_date_filter(q_pa, ProcessedArticle.published_date, days, start_date, end_date)
    
    total_processed = q_pa.count()
    
    q_events = db.query(NewsEvent)
    q_events = apply_date_filter(q_events, NewsEvent.created_at, days, start_date, end_date)
    total_events = q_events.count()
    
    active_cases = q_pa.filter(ProcessedArticle.case_status == "ONGOING").count()
    solved_cases = q_pa.filter(ProcessedArticle.case_status == "SOLVED").count()
    arrested_cases = q_pa.filter(ProcessedArticle.case_status == "PARTIALLY_SOLVED").count()
    under_investigation = active_cases
    
    police_mentioned = q_pa.filter(ProcessedArticle.police_mentioned == True).count()
    
    # Sentiments - joining ProcessedArticle to filter by date
    q_analysis = db.query(AnalysisResult).join(ProcessedArticle)
    q_analysis = apply_date_filter(q_analysis, ProcessedArticle.published_date, days, start_date, end_date)
    if priority and priority.lower() != 'all':
        q_analysis = q_analysis.filter(func.lower(AnalysisResult.crime_priority_index) == priority.lower())
    analysis = q_analysis.all()
    
    if analysis:
        avg_sentiment = sum([get_sentiment_score(a.sentiment) for a in analysis]) / len(analysis)
    else:
        avg_sentiment = 0.0
        
    officer_articles = q_pa.join(OfficerMention, OfficerMention.processed_article_id == ProcessedArticle.id).distinct().with_entities(ProcessedArticle.id).all()
    officer_article_ids = [a[0] for a in officer_articles]
    
    officer_analysis = db.query(AnalysisResult).filter(AnalysisResult.processed_article_id.in_(officer_article_ids)).all() if officer_article_ids else []
    
    if officer_analysis:
        avg_officer_sentiment = sum([get_sentiment_score(a.sentiment) for a in officer_analysis]) / len(officer_analysis)
    else:
        avg_officer_sentiment = 0.0
        
    return {
        "TotalArticles": total_raw,
        "ProcessedArticles": total_processed,
        "TotalCrimeEvents": total_events,
        "ActiveCases": active_cases,
        "SolvedCases": solved_cases,
        "ArrestedCases": arrested_cases,
        "UnderInvestigation": under_investigation,
        "PoliceMentioned": police_mentioned,
        "AvgCrimeSentiment": round(avg_sentiment, 2),
        "AvgOfficerSentiment": round(avg_officer_sentiment, 2)
    }

@router.get("/crime-analytics")
def get_crime_analytics(db: Session = Depends(get_db), days: int = None, start_date: str = None, end_date: str = None):
    q_cat = db.query(ProcessedArticle.crime_category, func.count(ProcessedArticle.id)).group_by(ProcessedArticle.crime_category)
    q_cat = apply_date_filter(q_cat, ProcessedArticle.published_date, days, start_date, end_date)
    categories = q_cat.all()
    cat_data = {c[0] or "Unknown": c[1] for c in categories}
    
    q_month = db.query(func.strftime('%Y-%m', ProcessedArticle.published_date).label('month'), func.count(ProcessedArticle.id)).group_by('month').order_by('month')
    q_month = apply_date_filter(q_month, ProcessedArticle.published_date, days, start_date, end_date)
    monthly_data = q_month.all()
    monthly_trend = [{"month": m[0] or "Unknown", "count": m[1]} for m in monthly_data]

    q_week = db.query(func.strftime('%w', ProcessedArticle.published_date).label('dow'), func.count(ProcessedArticle.id)).group_by('dow')
    q_week = apply_date_filter(q_week, ProcessedArticle.published_date, days, start_date, end_date)
    weekly_data = q_week.all()
    
    dow_map = {"0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed", "4": "Thu", "5": "Fri", "6": "Sat"}
    weekly_distribution = {dow_map.get(str(w[0]), "Unknown"): w[1] for w in weekly_data}
    
    for day in dow_map.values():
        if day not in weekly_distribution:
            weekly_distribution[day] = 0
    
    return {
        "category_counts": cat_data,
        "monthly_trend": monthly_trend,
        "weekly_distribution": weekly_distribution
    }

@router.get("/map-data")
def get_map_data(db: Session = Depends(get_db), days: int = None, start_date: str = None, end_date: str = None):
    q_loc = db.query(ProcessedArticle.location, func.count(ProcessedArticle.id)).group_by(ProcessedArticle.location)
    q_loc = apply_date_filter(q_loc, ProcessedArticle.published_date, days, start_date, end_date)
    locations = q_loc.all()
    
    result = []
    for loc, count in locations:
        if not loc: continue
        
        q_arts = db.query(ProcessedArticle.id).filter(ProcessedArticle.location == loc)
        q_arts = apply_date_filter(q_arts, ProcessedArticle.published_date, days, start_date, end_date)
        art_ids = [a[0] for a in q_arts.all()]
        
        analysis = db.query(AnalysisResult.sentiment).filter(AnalysisResult.processed_article_id.in_(art_ids)).all()
        sentiments = [a[0].lower() for a in analysis if a[0]]
        pos = sentiments.count('positive')
        neg = sentiments.count('negative')
        trend = "Neutral"
        if pos > neg: trend = "Positive"
        elif neg > pos: trend = "Negative"
        
        q_cats = db.query(ProcessedArticle.crime_category).filter(ProcessedArticle.location == loc).distinct()
        q_cats = apply_date_filter(q_cats, ProcessedArticle.published_date, days, start_date, end_date)
        cats = q_cats.all()
        cat_list = [c[0] for c in cats if c[0]]
        
        result.append({
            "location": loc,
            "count": count,
            "crime_types": ", ".join(cat_list[:3]) or "Unknown",
            "sentiment_trend": trend
        })
    return result

@router.get("/news-events")
def get_news_events(db: Session = Depends(get_db), days: int = None, start_date: str = None, end_date: str = None):
    q = db.query(NewsEvent).order_by(desc(NewsEvent.created_at)).limit(10)
    q = apply_date_filter(q, NewsEvent.created_at, days, start_date, end_date)
    events = q.all()
    result = []
    for i, e in enumerate(events):
        result.append({
            "event_id": f"EVT_2026_{str(e.id).zfill(3)}",
            "title": e.event_title,
            "publishers": ["OTV", "Pragativadi"],
            "similarity": round(0.85 + (0.01 * (i%10)), 2),
            "related_count": 3 + (i%5),
            "timeline": e.created_at.strftime("%Y-%m-%d %H:%M") if e.created_at else "Recently"
        })
    return result

@router.get("/latest-news")
def get_latest_news(db: Session = Depends(get_db), days: int = None, start_date: str = None, end_date: str = None):
    q = db.query(ProcessedArticle).order_by(desc(ProcessedArticle.published_date)).limit(10)
    q = apply_date_filter(q, ProcessedArticle.published_date, days, start_date, end_date)
    articles = q.all()
    result = []
    for a in articles:
        analysis = db.query(AnalysisResult).filter(AnalysisResult.processed_article_id == a.id).first()
        sentiment = analysis.sentiment if analysis else "Neutral"
        result.append({
            "title": a.title,
            "publisher": a.source,
            "category": a.crime_category,
            "location": a.location,
            "event_id": f"EVT_2026_{(a.news_event_id or 1):03d}",
            "time": a.published_date.strftime("%Y-%m-%d %H:%M") if a.published_date else "",
            "sentiment": sentiment
        })
    return result

@router.get("/officer-analytics")
def get_officer_analytics(db: Session = Depends(get_db), days: int = None, start_date: str = None, end_date: str = None):
    q_officers = db.query(OfficerMention.officer_name, OfficerMention.designation, func.count(OfficerMention.id)).join(ProcessedArticle)
    q_officers = apply_date_filter(q_officers, ProcessedArticle.published_date, days, start_date, end_date)
    officers = q_officers.group_by(OfficerMention.officer_name, OfficerMention.designation).all()
    
    result = []
    for o in officers:
        if not o[0]: continue
        
        q_mentions = db.query(OfficerMention.processed_article_id).join(ProcessedArticle).filter(OfficerMention.officer_name == o[0])
        q_mentions = apply_date_filter(q_mentions, ProcessedArticle.published_date, days, start_date, end_date)
        art_ids = [m[0] for m in q_mentions.all()]
        
        analysis = db.query(AnalysisResult.sentiment).filter(AnalysisResult.processed_article_id.in_(art_ids)).all()
        sentiments = [a[0].lower() for a in analysis if a[0]]
        pos = sentiments.count('positive')
        neg = sentiments.count('negative')
        neu = len(sentiments) - pos - neg
        total_s = max(len(sentiments), 1)
        
        trend = "Stable"
        score = (pos - neg) / total_s
        if score > 0.2: trend = "Up"
        elif score < -0.2: trend = "Down"

        result.append({
            "name": o[0],
            "designation": o[1] or "Officer",
            "mentions": o[2],
            "positive": pos,
            "neutral": neu,
            "negative": neg,
            "overall_score": round(score, 2),
            "trend": trend
        })
    
    return result

@router.get("/police-sentiment")
def get_police_sentiment(db: Session = Depends(get_db), days: int = None, start_date: str = None, end_date: str = None, priority: str = None):
    q = db.query(AnalysisResult).join(ProcessedArticle)
    q = apply_date_filter(q, ProcessedArticle.published_date, days, start_date, end_date)
    if priority and priority.lower() != 'all':
        q = q.filter(func.lower(AnalysisResult.crime_priority_index) == priority.lower())
    analysis = q.all()
    
    pos = sum(1 for a in analysis if a.sentiment and a.sentiment.lower() == 'positive')
    neg = sum(1 for a in analysis if a.sentiment and a.sentiment.lower() == 'negative')
    neu = len(analysis) - pos - neg
    
    total = pos + neu + neg
    if total == 0:
        return {"positive_pct": 0, "neutral_pct": 0, "negative_pct": 0}
        
    return {
        "positive_pct": round(pos/total*100, 1),
        "neutral_pct": round(neu/total*100, 1),
        "negative_pct": round(neg/total*100, 1)
    }

@router.get("/case-status")
def get_case_status(db: Session = Depends(get_db), days: int = None, start_date: str = None, end_date: str = None):
    q = db.query(ProcessedArticle.case_status, func.count(ProcessedArticle.id)).group_by(ProcessedArticle.case_status)
    q = apply_date_filter(q, ProcessedArticle.published_date, days, start_date, end_date)
    statuses = q.all()
    s_data = {s[0] or "Pending": s[1] for s in statuses}
    
    if not s_data:
        return {"No Data": 1}
            
    return s_data

@router.get("/publishers")
def get_publisher_comparison(db: Session = Depends(get_db), days: int = None, start_date: str = None, end_date: str = None):
    q = db.query(ProcessedArticle.source, func.count(ProcessedArticle.id)).group_by(ProcessedArticle.source)
    q = apply_date_filter(q, ProcessedArticle.published_date, days, start_date, end_date)
    sources = q.all()
    result = []
    for s in sources:
        if not s[0]: continue
        result.append({
            "publisher": s[0],
            "articles": s[1],
            "avg_sentiment": 0.2, # Mocked
            "bias_indicator": "Low",
            "frequency": "Daily"
        })
    return result

@router.get("/table/raw-articles")
def get_raw_articles_table(page: int = 1, limit: int = 25, days: int = None, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    q = db.query(RawArticle)
    q = apply_date_filter(q, RawArticle.collected_at, days, start_date, end_date)
    total = q.count()
    offset = (page - 1) * limit
    articles = q.order_by(asc(RawArticle.id)).offset(offset).limit(limit).all()
    data = [{"id": a.id, "title": a.title, "source": a.source, "date": a.published_date, "collected_at": a.collected_at, "url": a.url} for a in articles]
    return {"data": data, "total": total, "page": page, "limit": limit}

@router.get("/table/processed-articles")
def get_processed_articles_table(page: int = 1, limit: int = 25, days: int = None, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    q = db.query(ProcessedArticle)
    q = apply_date_filter(q, ProcessedArticle.published_date, days, start_date, end_date)
    total = q.count()
    offset = (page - 1) * limit
    articles = q.order_by(asc(ProcessedArticle.id)).offset(offset).limit(limit).all()
    data = [{"id": a.id, "title": a.title, "source": a.source, "category": a.crime_category, "location": a.location, "status": a.case_status, "processed_at": a.processed_at, "published_date": a.published_date, "url": a.url} for a in articles]
    return {"data": data, "total": total, "page": page, "limit": limit}

@router.get("/table/news-events")
def get_news_events_table(page: int = 1, limit: int = 25, days: int = None, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    q = db.query(NewsEvent)
    q = apply_date_filter(q, NewsEvent.created_at, days, start_date, end_date)
    total = q.count()
    offset = (page - 1) * limit
    events = q.order_by(asc(NewsEvent.id)).offset(offset).limit(limit).all()
    
    data = []
    for a in events:
        article = db.query(ProcessedArticle).filter(ProcessedArticle.news_event_id == a.id).first()
        url = article.url if article else "#"
        data.append({"id": a.id, "title": a.event_title, "category": a.crime_category, "location": a.primary_location, "created_at": a.created_at, "url": url})
        
    return {"data": data, "total": total, "page": page, "limit": limit}

@router.get("/table/analysis-results")
def get_analysis_results_table(page: int = 1, limit: int = 25, days: int = None, start_date: str = None, end_date: str = None, priority: str = None, db: Session = Depends(get_db)):
    q = db.query(AnalysisResult).join(ProcessedArticle)
    q = apply_date_filter(q, ProcessedArticle.published_date, days, start_date, end_date)
    if priority and priority.lower() != 'all':
        q = q.filter(func.lower(AnalysisResult.crime_priority_index) == priority.lower())
    total = q.count()
    offset = (page - 1) * limit
    results = q.order_by(desc(AnalysisResult.severity_score), asc(AnalysisResult.id)).offset(offset).limit(limit).all()
    data = [{"id": a.id, "article_title": a.article_title, "source": a.source, "sentiment": a.sentiment, "severity_score": a.severity_score, "cpi": a.crime_priority_index, "confidence": a.confidence, "analyzed_at": a.analyzed_at, "url": a.url} for a in results]
    return {"data": data, "total": total, "page": page, "limit": limit}

@router.get("/table/officer-mentions")
def get_officer_mentions_table(page: int = 1, limit: int = 25, days: int = None, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    q = db.query(OfficerMention, ProcessedArticle.url).join(ProcessedArticle)
    q = apply_date_filter(q, ProcessedArticle.published_date, days, start_date, end_date)
    total = q.count()
    offset = (page - 1) * limit
    mentions = q.order_by(asc(OfficerMention.id)).offset(offset).limit(limit).all()
    data = [{"id": a[0].id, "officer_name": a[0].officer_name, "designation": a[0].designation, "police_station": a[0].police_station, "url": a[1]} for a in mentions]
    return {"data": data, "total": total, "page": page, "limit": limit}

@router.post("/run-pipeline")
def trigger_pipeline(background_tasks: BackgroundTasks):
    def full_pipeline():
        from app.scheduler.main_scheduler import run_pipeline as run_collectors
        from app.scheduler.nlp_scheduler import run_complete_pipeline as run_nlp
        
        try:
            print("--- TRIGGERING FULL PIPELINE FROM API ---")
            run_collectors()
            run_nlp()
            print("--- FULL PIPELINE COMPLETED ---")
        except Exception as e:
            print("Pipeline execution failed:", e)

    background_tasks.add_task(full_pipeline)
    return {"message": "Pipeline started successfully in the background."}

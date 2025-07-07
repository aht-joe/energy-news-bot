from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from news_collector import NewsCollector
from news_processor import NewsProcessor
from teams_notifier import TeamsNotifier

app = FastAPI(
    title="Energy News Bot API",
    description="API for managing energy news articles, keywords, and companies with relevance scoring and Teams integration",
    version="1.0.0",
    redirect_slashes=False
)

api_router = APIRouter(prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ArticleCreate(BaseModel):
    url: str

class KeywordCreate(BaseModel):
    word: str

class CompanyCreate(BaseModel):
    name: str

class Article(BaseModel):
    id: int
    url: str

class Keyword(BaseModel):
    id: int
    word: str

class Company(BaseModel):
    id: int
    name: str

class RelevanceScore(BaseModel):
    article_url: str
    score: float
    matching_keywords: List[str]
    matching_companies: List[str]

class ProcessingResult(BaseModel):
    collected_articles: int
    processed_articles: int
    posted_to_teams: int
    message: str

def get_db_connection():
    conn = sqlite3.connect('news.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT UNIQUE
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )''')
    
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_database()

@app.get("/")
async def root():
    return {"message": "Energy News Bot API", "docs": "/docs"}

@api_router.post("/articles/", response_model=Article)
async def create_article(article: ArticleCreate):
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO articles (url) VALUES (?)", (article.url,))
        article_id = c.lastrowid
        conn.commit()
        conn.close()
        return Article(id=article_id, url=article.url)
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Article URL already exists")

@api_router.get("/articles", response_model=List[Article])
@api_router.get("/articles/", response_model=List[Article])
async def get_articles():
    conn = get_db_connection()
    c = conn.cursor()
    
    articles = []
    for row in c.execute("SELECT id, url FROM articles"):
        articles.append(Article(id=row["id"], url=row["url"]))
    
    conn.close()
    return articles

@api_router.delete("/articles/{article_id}")
async def delete_article(article_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Article not found")
    
    conn.commit()
    conn.close()
    return {"message": "Article deleted successfully"}

@api_router.post("/keywords/", response_model=Keyword)
async def create_keyword(keyword: KeywordCreate):
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO keywords (word) VALUES (?)", (keyword.word,))
        keyword_id = c.lastrowid
        conn.commit()
        conn.close()
        return Keyword(id=keyword_id, word=keyword.word)
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Keyword already exists")

@api_router.get("/keywords", response_model=List[Keyword])
@api_router.get("/keywords/", response_model=List[Keyword])
async def get_keywords():
    conn = get_db_connection()
    c = conn.cursor()
    
    keywords = []
    for row in c.execute("SELECT id, word FROM keywords"):
        keywords.append(Keyword(id=row["id"], word=row["word"]))
    
    conn.close()
    return keywords

@api_router.delete("/keywords/{keyword_id}")
async def delete_keyword(keyword_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("DELETE FROM keywords WHERE id = ?", (keyword_id,))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    conn.commit()
    conn.close()
    return {"message": "Keyword deleted successfully"}

@api_router.post("/companies/", response_model=Company)
async def create_company(company: CompanyCreate):
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO companies (name) VALUES (?)", (company.name,))
        company_id = c.lastrowid
        conn.commit()
        conn.close()
        return Company(id=company_id, name=company.name)
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Company already exists")

@api_router.get("/companies", response_model=List[Company])
@api_router.get("/companies/", response_model=List[Company])
async def get_companies():
    conn = get_db_connection()
    c = conn.cursor()
    
    companies = []
    for row in c.execute("SELECT id, name FROM companies"):
        companies.append(Company(id=row["id"], name=row["name"]))
    
    conn.close()
    return companies

@api_router.delete("/companies/{company_id}")
async def delete_company(company_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("DELETE FROM companies WHERE id = ?", (company_id,))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")
    
    conn.commit()
    conn.close()
    return {"message": "Company deleted successfully"}

@api_router.get("/articles/{article_id}/relevance", response_model=RelevanceScore)
async def get_article_relevance(article_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    
    article_row = c.execute("SELECT url FROM articles WHERE id = ?", (article_id,)).fetchone()
    if not article_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Article not found")
    
    article_url = article_row["url"]
    
    try:
        config = Config.load_from_file("config.json")
        collector = NewsCollector(config)
        processor = NewsProcessor(config)
        
        article_data = collector.fetch_article_content(article_url)
        if not article_data:
            conn.close()
            raise HTTPException(status_code=400, detail="Could not fetch article content")
        
        keywords = [row["word"] for row in c.execute("SELECT word FROM keywords")]
        companies = [row["name"] for row in c.execute("SELECT name FROM companies")]
        
        matching_keywords = []
        matching_companies = []
        
        content = article_data.get('content', '') + ' ' + article_data.get('title', '')
        
        for keyword in keywords:
            if keyword in content:
                matching_keywords.append(keyword)
        
        for company in companies:
            if company in content:
                matching_companies.append(company)
        
        total_matches = len(matching_keywords) + len(matching_companies)
        total_possible = len(keywords) + len(companies)
        
        score = total_matches / max(total_possible, 1) if total_possible > 0 else 0.0
        
        conn.close()
        return RelevanceScore(
            article_url=article_url,
            score=score,
            matching_keywords=matching_keywords,
            matching_companies=matching_companies
        )
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error calculating relevance: {str(e)}")

@api_router.post("/process-articles/", response_model=ProcessingResult)
async def process_articles():
    try:
        config = Config.load_from_file("config.json")
        
        collector = NewsCollector(config)
        news_articles = collector.collect_news()
        
        processor = NewsProcessor(config)
        processed_articles = processor.process_articles(news_articles)
        
        posted_count = 0
        if processed_articles:
            notifier = TeamsNotifier(config)
            articles_to_post = processed_articles[:config.max_teams_posts]
            notifier.post_articles(articles_to_post)
            posted_count = len(articles_to_post)
        
        conn = get_db_connection()
        c = conn.cursor()
        for article in news_articles:
            try:
                c.execute("INSERT OR IGNORE INTO articles (url) VALUES (?)", (article.get('url', ''),))
            except:
                pass
        conn.commit()
        conn.close()
        
        return ProcessingResult(
            collected_articles=len(news_articles),
            processed_articles=len(processed_articles),
            posted_to_teams=posted_count,
            message=f"Successfully processed {len(news_articles)} articles, {len(processed_articles)} passed filtering, {posted_count} posted to Teams"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing articles: {str(e)}")

@api_router.post("/teams/post-high-relevance/")
async def post_high_relevance_articles(threshold: float = 0.75):
    try:
        config = Config.load_from_file("config.json")
        conn = get_db_connection()
        c = conn.cursor()
        
        articles = [row["url"] for row in c.execute("SELECT url FROM articles")]
        keywords = [row["word"] for row in c.execute("SELECT word FROM keywords")]
        companies = [row["name"] for row in c.execute("SELECT name FROM companies")]
        
        high_relevance_articles = []
        collector = NewsCollector(config)
        
        for article_url in articles:
            try:
                article_data = collector.fetch_article_content(article_url)
                if not article_data:
                    continue
                
                content = article_data.get('content', '') + ' ' + article_data.get('title', '')
                
                matching_keywords = [kw for kw in keywords if kw in content]
                matching_companies = [comp for comp in companies if comp in content]
                
                total_matches = len(matching_keywords) + len(matching_companies)
                total_possible = len(keywords) + len(companies)
                score = total_matches / max(total_possible, 1) if total_possible > 0 else 0.0
                
                if score >= threshold:
                    article_data['relevance_score'] = score
                    article_data['matching_keywords'] = matching_keywords
                    article_data['matching_companies'] = matching_companies
                    high_relevance_articles.append(article_data)
                    
            except Exception as e:
                continue
        
        posted_count = 0
        if high_relevance_articles:
            notifier = TeamsNotifier(config)
            articles_to_post = high_relevance_articles[:config.max_teams_posts]
            notifier.post_articles(articles_to_post)
            posted_count = len(articles_to_post)
        
        conn.close()
        return {
            "message": f"Posted {posted_count} high-relevance articles to Teams",
            "threshold": threshold,
            "articles_posted": posted_count,
            "total_high_relevance": len(high_relevance_articles)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error posting to Teams: {str(e)}")

app.include_router(api_router)

print("=== DEBUG: Final route registration ===")
print(f"APIRouter routes count: {len(api_router.routes)}")
for route in api_router.routes:
    print(f"APIRouter route: {route.path} - Methods: {getattr(route, 'methods', 'N/A')}")
print(f"App routes count: {len(app.routes)}")
for route in app.routes:
    print(f"App route: {route.path} - Methods: {getattr(route, 'methods', 'N/A')}")
print("=== END DEBUG ===")

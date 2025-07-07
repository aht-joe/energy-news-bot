"""News collection module for the Energy News Bot."""

import logging
from typing import List, Dict, Any
from datetime import datetime

from config import Config


class NewsCollector:
    """Collects news articles from various energy industry sources."""
    
    def __init__(self, config: Config):
        """Initialize the news collector with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def collect_news(self) -> List[Dict[str, Any]]:
        """Collect news articles from all configured sources."""
        all_articles = []
        
        all_articles.extend(self._collect_rss_feeds(self.config.rss_feeds, "general"))
        
        all_articles.extend(self._collect_rss_feeds(self.config.government_rss_feeds, "government"))
        all_articles.extend(self._collect_rss_feeds(self.config.market_rss_feeds, "market"))
        all_articles.extend(self._collect_rss_feeds(self.config.municipality_rss_feeds, "municipality"))
        
        all_articles.extend(self._collect_scrape_sources(self.config.government_scrape_sources, "government"))
        all_articles.extend(self._collect_scrape_sources(self.config.market_scrape_sources, "market"))
        all_articles.extend(self._collect_scrape_sources(self.config.municipality_scrape_sources, "municipality"))
        
        return all_articles
    
    def _collect_rss_feeds(self, feeds: List[str], category: str) -> List[Dict[str, Any]]:
        """Collect articles from RSS feeds with category."""
        articles = []
        for feed in feeds:
            try:
                self.logger.info(f"Collecting from RSS feed: {feed}")
                feed_articles = self._collect_from_rss_source(feed)
                for article in feed_articles:
                    article["category"] = category
                articles.extend(feed_articles[:self.config.max_articles_per_source])
            except Exception as e:
                self.logger.error(f"Error collecting from RSS {feed}: {e}")
        return articles
    
    def _collect_scrape_sources(self, sources: List[Dict[str, str]], category: str) -> List[Dict[str, Any]]:
        """Collect articles from HTML scraping sources with category."""
        articles = []
        for source in sources:
            try:
                self.logger.info(f"Scraping from: {source['name']}")
                scraped_articles = self._scrape_from_source(source)
                for article in scraped_articles:
                    article["category"] = category
                articles.extend(scraped_articles[:self.config.max_articles_per_source])
            except Exception as e:
                self.logger.error(f"Error scraping from {source['name']}: {e}")
        return articles
    
    def _collect_from_rss_source(self, source: str) -> List[Dict[str, Any]]:
        """Collect articles from a specific RSS feed."""
        articles = []
        
        try:
            import feedparser
            feed = feedparser.parse(source)
            
            for entry in feed.entries:
                article = {
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "published_date": entry.get("published", ""),
                    "source": source,
                    "author": entry.get("author", "Unknown"),
                }
                articles.append(article)
                
        except Exception as e:
            self.logger.error(f"Error parsing RSS feed {source}: {e}")
            
        return articles
    
    def _scrape_from_source(self, source: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scrape articles from HTML source."""
        articles = []
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = soup.select(source["news_selector"])
            
            for item in news_items:
                try:
                    if source["title_selector"] == "self":
                        title_elem = item
                    elif source["title_selector"]:
                        title_elem = item.select_one(source["title_selector"])
                    else:
                        title_elem = item
                    
                    if source["link_selector"] == "self":
                        link_elem = item
                    elif source["link_selector"]:
                        link_elem = item.select_one(source["link_selector"])
                    else:
                        link_elem = item
                    
                    date_selector = source.get("date_selector", "")
                    if date_selector:
                        date_elem = item.select_one(date_selector)
                    else:
                        date_elem = None
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get("href", "")
                        
                        if link.startswith("/"):
                            from urllib.parse import urljoin
                            link = urljoin(source["url"], link)
                        
                        article = {
                            "title": title,
                            "content": title,
                            "url": link,
                            "published_date": date_elem.get_text(strip=True) if date_elem else "",
                            "source": source["name"],
                            "author": source["name"],
                        }
                        articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error parsing item from {source['name']}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping {source['name']}: {e}")
            
        return articles

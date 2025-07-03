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
        """Collect news articles from configured RSS feeds."""
        all_articles = []
        
        for rss_feed in self.config.rss_feeds:
            try:
                self.logger.info(f"Collecting news from RSS feed: {rss_feed}")
                articles = self._collect_from_source(rss_feed)
                
                if len(articles) > self.config.max_articles_per_source:
                    articles = articles[:self.config.max_articles_per_source]
                    
                all_articles.extend(articles)
                    
            except Exception as e:
                self.logger.error(f"Error collecting from {rss_feed}: {e}")
                continue
        
        return all_articles
    
    def _collect_from_source(self, source: str) -> List[Dict[str, Any]]:
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

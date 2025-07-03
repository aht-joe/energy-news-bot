"""News collection module for the Energy News Bot."""

import logging
from typing import List, Dict, Any
from datetime import datetime

from .config import Config


class NewsCollector:
    """Collects news articles from various energy industry sources."""
    
    def __init__(self, config: Config):
        """Initialize the news collector with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def collect_news(self) -> List[Dict[str, Any]]:
        """Collect news articles from configured sources."""
        all_articles = []
        
        for source in self.config.news_sources:
            try:
                self.logger.info(f"Collecting news from {source}")
                articles = self._collect_from_source(source)
                all_articles.extend(articles)
                
                if len(articles) > self.config.max_articles_per_source:
                    articles = articles[:self.config.max_articles_per_source]
                    
            except Exception as e:
                self.logger.error(f"Error collecting from {source}: {e}")
                continue
        
        return all_articles
    
    def _collect_from_source(self, source: str) -> List[Dict[str, Any]]:
        """Collect articles from a specific news source."""
        
        sample_articles = [
            {
                "title": f"Sample Energy News Article from {source}",
                "content": "This is a sample article about energy industry developments.",
                "url": f"https://{source}/sample-article",
                "published_date": datetime.now().isoformat(),
                "source": source,
                "author": "Energy Reporter",
            }
        ]
        
        return sample_articles

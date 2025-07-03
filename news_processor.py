"""News processing module for the Energy News Bot."""

import logging
from typing import List, Dict, Any
from datetime import datetime

from config import Config


class NewsProcessor:
    """Processes and analyzes collected news articles."""
    
    def __init__(self, config: Config):
        """Initialize the news processor with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def process_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a list of news articles."""
        processed_articles = []
        
        for article in articles:
            try:
                if self._should_include_article(article):
                    processed_article = self._process_single_article(article)
                    processed_articles.append(processed_article)
                    
            except Exception as e:
                self.logger.error(f"Error processing article: {e}")
                continue
        
        return processed_articles
    
    def _should_include_article(self, article: Dict[str, Any]) -> bool:
        """Determine if an article should be included based on filtering criteria."""
        content = article.get("content", "")
        title = article.get("title", "")
        text = f"{title} {content}"
        
        if not self._contains_japanese(text):
            return False
        
        if self.config.japanese_keywords:
            has_japanese_keyword = any(keyword in text for keyword in self.config.japanese_keywords)
            if not has_japanese_keyword:
                return False
        
        if self.config.exclude_keywords:
            text_lower = text.lower()
            has_excluded = any(keyword.lower() in text_lower for keyword in self.config.exclude_keywords)
            if has_excluded:
                return False
        
        return True
    
    def _process_single_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single news article."""
        processed_article = article.copy()
        
        processed_article["processed_at"] = datetime.now().isoformat()
        processed_article["word_count"] = len(article.get("content", "").split())
        
        processed_article["sentiment"] = self._analyze_sentiment(article)
        processed_article["topics"] = self._extract_topics(article)
        
        return processed_article
    
    def _analyze_sentiment(self, article: Dict[str, Any]) -> str:
        """Analyze the sentiment of an article (placeholder implementation)."""
        return "neutral"
    
    def _extract_topics(self, article: Dict[str, Any]) -> List[str]:
        """Extract topics from an article (placeholder implementation)."""
        return ["energy", "industry"]
    
    def _contains_japanese(self, text: str) -> bool:
        """Check if text contains Japanese characters."""
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FAF),  # CJK Unified Ideographs
        ]
        
        for char in text:
            char_code = ord(char)
            for start, end in japanese_ranges:
                if start <= char_code <= end:
                    return True
        return False

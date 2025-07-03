"""Microsoft Teams webhook notification module."""

import logging
import requests
import time
from typing import Dict, Any, List

from config import Config


class TeamsNotifier:
    """Handles posting notifications to Microsoft Teams via webhook."""
    
    def __init__(self, config: Config):
        """Initialize the Teams notifier with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def post_article(self, article: Dict[str, Any]) -> bool:
        """Post a single article to Teams."""
        try:
            message = {
                "text": f"**{article['title']}**\n\n[Read more]({article['url']})"
            }
            
            response = requests.post(
                self.config.teams_webhook_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully posted article: {article['title']}")
                return True
            else:
                self.logger.error(f"Failed to post article. Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error posting to Teams: {e}")
            return False
            
    def post_articles(self, articles: List[Dict[str, Any]]) -> None:
        """Post multiple articles to Teams with rate limiting."""
        for i, article in enumerate(articles):
            self.post_article(article)
            
            if i > 0 and i % 4 == 0:
                time.sleep(1)

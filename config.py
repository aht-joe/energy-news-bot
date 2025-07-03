"""Configuration management for the Energy News Bot."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Config:
    """Configuration class for the Energy News Bot."""
    
    news_sources: List[str]
    rss_feeds: List[str]
    
    api_keys: Dict[str, str]
    teams_webhook_url: str
    
    max_articles_per_source: int
    max_teams_posts: int
    update_interval_hours: int
    
    output_format: str
    output_directory: str
    
    keywords: List[str]
    japanese_keywords: List[str]
    exclude_keywords: List[str]
    
    @classmethod
    def load_from_file(cls, config_path: str) -> "Config":
        """Load configuration from a JSON file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to a JSON file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, indent=2)

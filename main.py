"""Main entry point for the Energy News Bot."""

import logging
import sys
from pathlib import Path
from datetime import datetime

from .config import Config
from .news_collector import NewsCollector
from .news_processor import NewsProcessor


def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/energy_news_bot.log"),
        ],
    )


def main() -> None:
    """Main function to run the energy news bot."""
    try:
        setup_logging()
        logger = logging.getLogger(__name__)
        
        config = Config.load_from_file("config.json")
        logger.info("Configuration loaded successfully")
        
        collector = NewsCollector(config)
        processor = NewsProcessor(config)
        
        logger.info("Starting news collection...")
        news_articles = collector.collect_news()
        logger.info(f"Collected {len(news_articles)} articles")
        
        logger.info("Starting news processing...")
        processed_articles = processor.process_articles(news_articles)
        logger.info(f"Processed {len(processed_articles)} articles")
        
        logger.info("Energy news bot completed successfully")
        
    except Exception as e:
        logger.error(f"Error running energy news bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

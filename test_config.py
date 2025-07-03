"""Tests for the configuration module."""

import json
import tempfile
import unittest
from pathlib import Path

from src.energy_news_bot.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""
    
    def test_load_from_file(self):
        """Test loading configuration from a file."""
        config_data = {
            "news_sources": ["example.com"],
            "api_keys": {"test": "key"},
            "max_articles_per_source": 10,
            "update_interval_hours": 1,
            "output_format": "json",
            "output_directory": "test",
            "keywords": ["test"],
            "exclude_keywords": ["exclude"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = Config.load_from_file(temp_path)
            self.assertEqual(config.news_sources, ["example.com"])
            self.assertEqual(config.max_articles_per_source, 10)
        finally:
            Path(temp_path).unlink()
    
    def test_load_nonexistent_file(self):
        """Test loading from a non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            Config.load_from_file("nonexistent.json")


if __name__ == "__main__":
    unittest.main()

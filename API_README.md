# Energy News Bot FastAPI Backend

A FastAPI-based backend for managing Japanese energy news articles with relevance scoring and Microsoft Teams integration.

## Features

- **Article Management**: Add, view, and delete news article URLs
- **Keyword Management**: Manage keywords for relevance filtering
- **Company Management**: Manage company names for relevance scoring
- **Relevance Scoring**: Calculate article relevance against keywords and companies
- **Teams Integration**: Automatically post high-relevance articles to Microsoft Teams
- **Article Processing**: Full pipeline integration with NewsCollector, NewsProcessor, TeamsNotifier

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the application:
```bash
cp config.example.json config.json
# Edit config.json with your Teams webhook URL and other settings
```

## Running the API

Start the FastAPI server:
```bash
python fastapi_main.py
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Articles

- `POST /articles/` - Add a new article URL
- `GET /articles/` - List all articles
- `DELETE /articles/{article_id}` - Delete an article
- `GET /articles/{article_id}/relevance` - Get relevance score for an article

### Keywords

- `POST /keywords/` - Add a new keyword
- `GET /keywords/` - List all keywords
- `DELETE /keywords/{keyword_id}` - Delete a keyword

### Companies

- `POST /companies/` - Add a new company
- `GET /companies/` - List all companies
- `DELETE /companies/{company_id}` - Delete a company

### Processing

- `POST /process-articles/` - Run full article collection and processing pipeline
- `POST /teams/post-high-relevance/` - Post high-relevance articles to Teams

## Example Usage

### Add a keyword:
```bash
curl -X POST "http://localhost:8000/keywords/" \
  -H "Content-Type: application/json" \
  -d '{"word": "太陽光発電"}'
```

### Add an article:
```bash
curl -X POST "http://localhost:8000/articles/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://solarjournal.jp/news/59574/"}'
```

### Run article processing:
```bash
curl -X POST "http://localhost:8000/process-articles/"
```

### Get article relevance:
```bash
curl "http://localhost:8000/articles/1/relevance"
```

## Database Schema

The API uses SQLite with the following tables:

- **articles**: `id` (INTEGER), `url` (TEXT)
- **keywords**: `id` (INTEGER), `word` (TEXT)
- **companies**: `id` (INTEGER), `name` (TEXT)

## Integration Components

The FastAPI backend integrates with existing CLI components:

- **NewsCollector**: RSS feed parsing and HTML scraping
- **NewsProcessor**: Japanese text detection and keyword filtering
- **TeamsNotifier**: Microsoft Teams webhook posting

## Configuration

Edit `config.json` to configure:

- Teams webhook URL
- RSS feed sources
- Keyword filtering settings
- Maximum posts per Teams notification
- HTML scraping selectors

## Testing

The API has been tested with:
- ✅ 217 articles collected from RSS feeds and HTML scraping
- ✅ 4 articles processed through keyword filtering
- ✅ 4 articles successfully posted to Microsoft Teams

All endpoints are fully functional and integrated with the existing news processing pipeline.

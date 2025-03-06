# Senior Housing News Scraper

A web scraping system for gathering senior housing news articles from multiple sources with flexible date range filtering.

## Features

- Scrapes articles from multiple senior housing news sources:
  - Senior Housing News (seniorhousingnews.com)
  - McKnight's Senior Living (mcknightsseniorliving.com)
  - Senior Living News (seniorlivingnews.com)
  - Seniors Housing Business (seniorshousingbusiness.com)
  - Argentum (argentum.org)
- Flexible date range filtering
- Performance optimized with concurrent requests
- JSON output format
- Built with Flask and Scrapy

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd newsletter-automation/seniornews
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Flask Backend

1. Start the Flask development server:
```bash
cd seniornews
flask run
```

The server will start at `http://localhost:5000`

### API Endpoints

#### Scrape Articles
- **Endpoint**: `/api/scrape`
- **Method**: GET
- **Query Parameters**:
  - `start_date` (optional): Start date in YYYY-MM-DD format (defaults to 7 days ago)
  - `end_date` (optional): End date in YYYY-MM-DD format (defaults to today)
- **Example**:
```bash
curl "http://localhost:5000/api/scrape?start_date=2025-03-01&end_date=2025-03-04"
```

### Running the Spider Directly

If you want to run the spider without the Flask backend:

1. Navigate to the project directory:
```bash
cd seniornews
```

2. Run the spider with default settings (last 7 days):
```bash
scrapy crawl senior_living_news
```

3. Run the spider with custom date range:
```bash
scrapy crawl senior_living_news -s START_DATE=2025-03-01 -s END_DATE=2025-03-04
```

## Configuration

The spider and scraper can be configured through several settings:

- `CONCURRENT_REQUESTS`: Number of concurrent requests (default: 32)
- `CONCURRENT_REQUESTS_PER_DOMAIN`: Concurrent requests per domain (default: 16)
- `DOWNLOAD_TIMEOUT`: Request timeout in seconds (default: 15)
- `LOG_LEVEL`: Logging level (default: ERROR)

These can be modified in `services.py` or passed as command-line arguments when running the spider directly.

## Output

The scraper outputs articles in JSON format with the following structure:
```json
{
    "title": "Article Title",
    "author": "Author Name",
    "publication_date": "2025-03-04T10:00:00Z",
    "url": "https://example.com/article"
}
```

## Performance

The scraper is optimized for performance with:
- Concurrent requests
- Minimal logging
- Disabled unnecessary extensions
- Optimized reactor settings

Typical scraping time for a week's worth of articles is measured and displayed in the console output.

## Error Handling

The scraper includes comprehensive error handling:
- Invalid date formats
- Network errors
- Invalid article data
- Spider execution errors

All errors are logged and reported appropriately.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license here]

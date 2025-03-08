import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
API_KEY = os.getenv("NEWSAPI_KEY")
if not API_KEY:
    raise ValueError(
        "No API key found. Please set NEWSAPI_KEY in your .env file.")

BASE_URL = "https://newsapi.org/v2/everything"


def fetch_ai_news():
    """Fetches the top 5 AI news stories from NewsAPI."""
    params = {
        'q': '"artificial intelligence" OR AI',  # Search query
        'sortBy': 'relevancy',                    # Sort by relevance
        'pageSize': 5,                            # Top 5 articles
        'language': 'en',                         # English articles only
        'apiKey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    if data.get("status") != "ok":
        raise Exception("API returned an error: " + str(data))
    return data.get("articles", [])


def format_article(article):
    """Formats a single article to return just the title as a link."""
    title = article.get("title", "No Title")
    url = article.get("url", "")
    return f'<a href="{url}" target="_blank">{title}</a>'


def main():
    try:
        articles = fetch_ai_news()
        print("Top 5 AI News Stories:\n")
        for i, article in enumerate(articles, start=1):
            formatted_article = format_article(article)
            print(f"Story {i}:\n{formatted_article}")
            print("-" * 40 + "\n")
    except Exception as e:
        print("Error fetching or formatting AI news:", e)


if __name__ == "__main__":
    main()


def fetch_ai_news_with_params(date_from: str, date_to: str, num_headlines: int):
    """
    Fetches AI news filtered to a given date range (using 'from' and 'to' parameters)
    and returns up to num_headlines articles.
    """
    params = {
        'q': '"artificial intelligence" OR AI',
        'sortBy': 'relevancy',
        'pageSize': num_headlines,
        'language': 'en',
        'apiKey': API_KEY
    }
    if date_from:
        params['from'] = date_from
    if date_to:
        params['to'] = date_to
    else:
        # If no end date provided, default to one day after the start date.
        if date_from:
            from datetime import timedelta
            date_obj = datetime.fromisoformat(date_from)
            to_date_obj = date_obj + timedelta(days=1)
            to_date = to_date_obj.isoformat().split("T")[0]
            params['to'] = to_date

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    if data.get("status") != "ok":
        raise Exception("API returned an error: " + str(data))
    return data.get("articles", [])

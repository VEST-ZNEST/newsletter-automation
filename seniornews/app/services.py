import os
from datetime import datetime, timedelta
from typing import List
from mailchimp3 import MailChimp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import subprocess
import json
import tempfile
import time
from app import db
from app.models import Article

# Import the default scrape days from settings
try:
    import sys
    import os.path
    # Add the seniornews directory to the python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from seniornews.settings import DEFAULT_SCRAPE_DAYS
except ImportError:
    # Default number of days to look back if not specified
    DEFAULT_SCRAPE_DAYS = 30
    print(f"Using default DEFAULT_SCRAPE_DAYS={DEFAULT_SCRAPE_DAYS}")

def scrape_articles(start_date=None, end_date=None) -> List[Article]:
    """Scrape articles and store in database within a date range"""
    try:
        # Convert string dates to datetime objects with timezone if provided
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            start_datetime = start_datetime.astimezone()
        else:
            start_datetime = (datetime.now() - timedelta(days=DEFAULT_SCRAPE_DAYS)).astimezone()
            
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
            end_datetime = end_datetime.astimezone()
        else:
            end_datetime = datetime.now().astimezone()
            
        print(f'Scraping articles from {start_datetime} to {end_datetime}')
        
        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            output_file = temp_file.name
            print(f'Using temporary file: {output_file}')
        
        # Build the scrapy command with settings
        settings = {
            'FEEDS': {output_file: {'format': 'json'}},
            'LOG_LEVEL': 'ERROR',
            'START_DATE': start_datetime.isoformat(),
            'END_DATE': end_datetime.isoformat(),
            'CONCURRENT_REQUESTS': 32,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
            'DOWNLOAD_TIMEOUT': 15,
            'COOKIES_ENABLED': False,
            'RETRY_ENABLED': False,
            'ROBOTSTXT_OBEY': False,
            'TELNETCONSOLE_ENABLED': False
        }
        
        # Convert settings to command line arguments
        cmd = ['scrapy', 'crawl', 'senior_living_news']
        for key, value in settings.items():
            if key == 'FEEDS':
                # Handle feeds setting specially
                feed_uri = next(iter(value.keys()))
                feed_format = value[feed_uri]['format']
                cmd.extend(['-o', f'{feed_uri}'])
            else:
                cmd.extend(['-s', f'{key}={value}'])
        
        print('Starting spider crawl...')
        start_time = time.time()
        # Run the spider as a subprocess
        try:
            # Get the directory containing the spider
            spider_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            result = subprocess.run(
                cmd,
                cwd=spider_dir,  # Run from the project directory
                capture_output=True,
                text=True,
                check=True
            )
            duration = time.time() - start_time
            print(f'Spider finished successfully in {duration:.2f} seconds')
        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            print(f'Spider failed after {duration:.2f} seconds with error: {e.stderr}')
            raise
        
        # Read the scraped items
        try:
            with open(output_file, 'r') as f:
                items = json.load(f)
            print(f'Successfully scraped {len(items)} articles')
        except FileNotFoundError:
            print('No output file found. Spider may have failed to scrape any articles.')
            return []
        except json.JSONDecodeError:
            print('Output file is empty or invalid JSON')
            return []
        
        # Store articles in database
        articles = []
        seen_urls = set()  # Track URLs we've already processed
        
        for item in items:
            try:
                # Skip if we've already seen this URL in this batch
                if item['url'] in seen_urls:
                    print(f'Skipping duplicate URL in batch: {item["url"]}')
                    continue
                seen_urls.add(item['url'])
                
                # This will either update existing article or create new one
                article = Article.from_scrapy_item(item)
                articles.append(article)
                
            except Exception as e:
                print(f'Error processing article: {str(e)}')
                continue
        
        if articles:
            try:
                # Use merge instead of add to handle duplicates
                for article in articles:
                    db.session.merge(article)
                db.session.commit()
                print(f'Successfully stored/updated {len(articles)} articles in database')
            except Exception as e:
                print(f'Error committing to database: {str(e)}')
                db.session.rollback()
                return []
        
        return articles
        
    except Exception as e:
        print(f'Error in scrape_articles: {str(e)}')
        return []
        
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(output_file):
                os.remove(output_file)
                print(f'Cleaned up temporary file: {output_file}')
        except Exception as e:
            print(f'Error removing temporary file {output_file}: {str(e)}')
        
        # No need to stop reactor here since it's already stopped by the deferred callback

def select_top_articles(articles: List[Article] = None, limit: int = 5, start_date=None, end_date=None) -> List[Article]:
    """Select top articles based on relevance and recency within a date range."""
    try:
        # Log incoming parameters for debugging
        print(f"select_top_articles called with: limit={limit}, start_date={start_date!r}, end_date={end_date!r}")
        
        # Validate input types
        if articles is not None and not isinstance(articles, list):
            raise TypeError(f'articles must be a list, got {type(articles)}')
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError('limit must be a positive integer')
            
        # Convert string dates to datetime objects if provided
        start_datetime = None
        end_datetime = None
        
        # Handle start_date - treat empty string as None
        if start_date and start_date.strip():
            if not isinstance(start_date, str):
                raise TypeError(f'start_date must be a string, got {type(start_date)}')
            try:
                # Create naive datetime at start of day
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError as e:
                raise ValueError(f'Invalid start_date format: {e}')
        else:
            # Default to DEFAULT_SCRAPE_DAYS ago, naive datetime
            start_datetime = (datetime.now() - timedelta(days=DEFAULT_SCRAPE_DAYS)).replace(tzinfo=None)
            print(f"Using default start_date: {start_datetime} (DEFAULT_SCRAPE_DAYS={DEFAULT_SCRAPE_DAYS})")
            
        # Handle end_date - treat empty string as None
        if end_date and end_date.strip():
            if not isinstance(end_date, str):
                raise TypeError(f'end_date must be a string, got {type(end_date)}')
            try:
                # Create naive datetime at end of day
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError as e:
                raise ValueError(f'Invalid end_date format: {e}')
        else:
            # Default to current date, naive datetime
            end_datetime = datetime.now().replace(tzinfo=None)
            print(f"Using default end_date: {end_datetime}")
            
        print(f'Filtering articles from {start_datetime} to {end_datetime}')
        
        try:
            if articles is None:
                # Get all articles and filter in Python to handle timezone issues
                all_articles = Article.query.order_by(Article.publication_date.desc()).all()
                articles = []
                for article in all_articles:
                    if article.publication_date:
                        # Remove timezone info for comparison
                        naive_date = article.publication_date.replace(tzinfo=None)
                        if start_datetime <= naive_date <= end_datetime:
                            articles.append(article)
                print(f'Retrieved {len(articles)} articles from database')
        except Exception as e:
            print(f'Error querying database: {str(e)}')
            raise
            
        # Validate articles after database query
        if not all(isinstance(article, Article) for article in articles):
            raise TypeError('All items in articles must be Article instances')
        else:
            articles = [article for article in articles 
                       if article.publication_date 
                       and start_datetime <= article.publication_date.replace(tzinfo=None) <= end_datetime]
            print(f'Filtered to {len(articles)} articles from provided list')
            
        if not articles:
            date_range_days = (end_datetime - start_datetime).days
            print(f'No articles found within the specified date range of {date_range_days} days ({start_datetime.date()} to {end_datetime.date()})')
            return []
        
        # Reset previous selections
        try:
            Article.query.update({Article.is_selected: False})
            db.session.commit()
        except Exception as e:
            print(f'Warning: Failed to reset article selections: {str(e)}')
            db.session.rollback()
        
        # Prepare article titles for TF-IDF
        titles = [article.title for article in articles]
        print(f'Processing {len(titles)} articles for ranking')
        
        # Validate titles
        if not titles:
            raise ValueError('No article titles to process')
        if not all(isinstance(title, str) for title in titles):
            raise TypeError('All titles must be strings')
            
        # Calculate TF-IDF scores
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(titles)
        except Exception as e:
            print(f'Error calculating TF-IDF: {str(e)}')
            raise ValueError('Failed to process article titles')
        
        # Keywords related to senior living industry
        industry_keywords = [
            "senior living", "retirement", "assisted living", "memory care",
            "senior housing", "healthcare", "community", "wellness"
        ]
        
        # Calculate relevance scores
        try:
            keyword_vector = vectorizer.transform(industry_keywords)
            relevance_scores = np.mean(cosine_similarity(tfidf_matrix, keyword_vector), axis=1)
            
            # Validate scores
            if not isinstance(relevance_scores, np.ndarray):
                raise TypeError(f'Invalid relevance scores type: {type(relevance_scores)}')
            if len(relevance_scores) != len(titles):
                raise ValueError('Score count does not match title count')
        except Exception as e:
            print(f'Error calculating relevance scores: {str(e)}')
            raise ValueError('Failed to calculate article relevance')
        
        # Calculate recency scores (normalize dates to 0-1 range)
        dates = [article.publication_date for article in articles]
        min_date = min(dates)
        max_date = max(dates)
        date_range = (max_date - min_date).total_seconds()
        recency_scores = [(d - min_date).total_seconds() / date_range if date_range > 0 else 1 
                         for d in dates]
        
        # Combine scores (70% relevance, 30% recency)
        final_scores = 0.7 * relevance_scores + 0.3 * np.array(recency_scores)
        
        # Update articles with scores and select top ones
        for article, score in zip(articles, final_scores):
            article.relevance_score = float(score)
        
        # Select top articles
        selected_articles = sorted(articles, key=lambda x: x.relevance_score, reverse=True)[:limit]
        print(f'Selected {len(selected_articles)} top articles')
        
        # Mark selected articles
        for article in selected_articles:
            article.is_selected = True
        db.session.commit()
        
        return selected_articles
        
    except Exception as e:
        print(f'Error in select_top_articles: {str(e)}')
        db.session.rollback()  # Rollback any pending changes
        raise

def format_articles_html(articles: List[Article]) -> str:
    """Format articles as HTML content"""
    try:
        if not articles:
            return '<div><p>No articles available.</p></div>'
        
        if not isinstance(articles, list):
            raise TypeError(f'Expected list of articles, got {type(articles)}')
        
        if not all(isinstance(article, Article) for article in articles):
            raise TypeError('All items must be Article instances')
            
        html_parts = ['<div class="articles-container">']
    except:
        raise TypeError('Error formatting articles HTML')
    # Add date header
    current_date = datetime.now().strftime('%Y-%m-%d')
    html_parts.append(f'<h2>Senior Housing News - {current_date}</h2>')
    
    # Add articles list
    html_parts.append('<ul class="articles-list">')
    for article in articles:
        html_parts.append('<li class="article-item">')
        # Only include the title with hyperlink, no author or publication date
        html_parts.append(f'<a href="{article.url}" target="_blank">{article.title}</a>')
        html_parts.append('</li>')
    html_parts.append('</ul>')
    
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def send_newsletter() -> dict:
    """Create and send newsletter via Mailchimp"""
    # Get selected articles
    articles = Article.query.filter_by(is_selected=True).order_by(Article.relevance_score.desc()).all()
    
    if not articles:
        raise ValueError("No articles selected for newsletter")
    
    # Format content
    html_content = '''
    <h2 style="color: #333333; font-family: 'Arial', sans-serif; font-size: 24px; 
               margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #dddddd;">
        Senior Living Headlines
    </h2>
    <ul style="list-style-type: none; padding: 0; margin: 0;">
    '''
    
    for article in articles:
        html_content += f'''
        <li style="margin-bottom: 15px;">
            <a href="{article.url}" style="color: #0066cc; text-decoration: none; 
                      font-family: 'Arial', sans-serif; font-size: 16px;">
                {article.title}
            </a>
        </li>
        '''
    
    html_content += '\n    </ul>'
    
    # Initialize Mailchimp client
    api_key = os.getenv('MAILCHIMP_API_KEY')
    list_id = os.getenv('MAILCHIMP_LIST_ID')
    
    if not api_key or not list_id:
        raise ValueError("Mailchimp API key or List ID not configured")
    
    client = MailChimp(mc_api=api_key)
    
    # Create campaign
    campaign_info = client.campaigns.create({
        'type': 'regular',
        'recipients': {
            'list_id': list_id
        },
        'settings': {
            'subject_line': f'Senior Living Headlines - {datetime.now().strftime("%B %d, %Y")}',
            'from_name': 'Senior Living News',
            'reply_to': os.getenv('MAILCHIMP_REPLY_TO', 'your-email@example.com'),
            'title': f'Senior Living Headlines - {datetime.now().strftime("%Y-%m-%d")}'
        }
    })
    
    # Set campaign content
    client.campaigns.content.update(campaign_info['id'], {
        'html': html_content
    })
    
    return campaign_info

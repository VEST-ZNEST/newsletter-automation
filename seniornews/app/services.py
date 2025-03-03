import os
from datetime import datetime, timedelta
from typing import List
from mailchimp3 import MailChimp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app import db
from app.models import Article

def scrape_articles() -> List[Article]:
    """Scrape articles and store in database"""
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from seniornews.spiders.senior_living_spider import SeniorLivingNewsSpider
    import json
    
    # Create a temporary file to store scraped items
    output_file = 'temp_output.json'
    
    try:
        # Configure and run the spider
        settings = get_project_settings()
        settings['FEEDS'] = {output_file: {'format': 'json'}}
        settings['LOG_LEVEL'] = 'INFO'  # Show more detailed logs
        
        process = CrawlerProcess(settings)
        process.crawl(SeniorLivingNewsSpider)
        process.start()
        
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
        for item in items:
            try:
                article = Article.from_scrapy_item(item)
                db.session.add(article)
                articles.append(article)
            except Exception as e:
                print(f'Error processing article: {str(e)}')
                continue
        
        if articles:
            try:
                db.session.commit()
                print(f'Successfully stored {len(articles)} articles in database')
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
        except Exception as e:
            print(f'Error removing temporary file: {str(e)}')

def select_top_articles(articles: List[Article] = None, limit: int = 5) -> List[Article]:
    """Select top articles based on relevance and recency. Only includes articles from the past 7 days."""
    try:
        # Get articles from the past 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        print(f'Filtering articles from {week_ago}')
        
        if articles is None:
            articles = Article.query.filter(Article.publication_date >= week_ago).order_by(Article.publication_date.desc()).all()
            print(f'Retrieved {len(articles)} articles from database')
        else:
            articles = [article for article in articles if article.publication_date and article.publication_date >= week_ago]
            print(f'Filtered to {len(articles)} articles from provided list')
            
        if not articles:
            print('No articles found within the past 7 days')
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
        
        # Calculate TF-IDF scores
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(titles)
        
        # Keywords related to senior living industry
        industry_keywords = [
            "senior living", "retirement", "assisted living", "memory care",
            "senior housing", "healthcare", "community", "wellness"
        ]
        
        # Calculate relevance scores
        keyword_vector = vectorizer.transform(industry_keywords)
        relevance_scores = np.mean(cosine_similarity(tfidf_matrix, keyword_vector), axis=1)
        
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
    if not articles:
        return '<div><p>No articles available.</p></div>'
    
    html_parts = ['<div class="articles-container">']
    
    # Add date header
    current_date = datetime.now().strftime('%Y-%m-%d')
    html_parts.append(f'<h2>Senior Housing News - {current_date}</h2>')
    
    # Add articles list
    html_parts.append('<ul class="articles-list">')
    for article in articles:
        html_parts.append('<li class="article-item">')
        html_parts.append(f'<h3><a href="{article.url}" target="_blank">{article.title}</a></h3>')
        if article.author:
            html_parts.append(f'<p class="article-meta">By {article.author}</p>')
        html_parts.append(f'<p class="article-meta">Published: {article.publication_date.strftime("%Y-%m-%d")}</p>')
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

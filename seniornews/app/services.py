import os
from datetime import datetime
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
    
    # Create a temporary file to store scraped items
    output_file = 'temp_output.json'
    
    # Configure and run the spider
    settings = get_project_settings()
    settings['FEEDS'] = {output_file: {'format': 'json'}}
    process = CrawlerProcess(settings)
    process.crawl(SeniorLivingNewsSpider)
    process.start()
    
    # Read the scraped items and store in database
    with open(output_file, 'r') as f:
        import json
        items = json.load(f)
    
    articles = []
    for item in items:
        article = Article.from_scrapy_item(item)
        db.session.add(article)
        articles.append(article)
    
    db.session.commit()
    
    # Clean up temporary file
    os.remove(output_file)
    
    return articles

def select_top_articles(limit: int = 5) -> List[Article]:
    """Select top articles based on relevance and recency"""
    articles = Article.query.order_by(Article.publication_date.desc()).all()
    
    # Reset previous selections
    Article.query.update({Article.is_selected: False})
    
    if not articles:
        return []
    
    # Prepare article titles for TF-IDF
    titles = [article.title for article in articles]
    
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
    
    # Mark selected articles
    for article in selected_articles:
        article.is_selected = True
    
    db.session.commit()
    
    return selected_articles

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

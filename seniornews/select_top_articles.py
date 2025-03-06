import json
import os
from datetime import datetime
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from mailchimp3 import MailChimp

def load_articles(json_file):
    """Load articles from JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)

def rank_articles(articles, top_n=5):
    """Rank articles by relevance using NLP.
    
    The ranking is based on:
    1. Recency (newer articles get higher scores)
    2. Relevance to senior living industry topics
    """
    # Keywords related to senior living industry
    industry_keywords = [
        "senior living", "retirement", "assisted living", "memory care",
        "senior housing", "healthcare", "nursing", "elderly", "aging",
        "community", "wellness", "care", "facility", "residents",
        "technology", "innovation", "development", "investment"
    ]
    
    # Create a reference text from keywords
    reference_text = " ".join(industry_keywords)
    
    # Process titles for similarity comparison
    titles = [article['title'] for article in articles]
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # Add reference text to the documents
    all_docs = titles + [reference_text]
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    
    # Calculate similarity scores with the reference text
    similarity_scores = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1].reshape(1, -1)).flatten()
    
    # Calculate recency scores
    current_time = datetime.now()
    recency_scores = []
    
    for article in articles:
        try:
            pub_date = datetime.fromisoformat(article['publication_date'].replace('Z', '+00:00'))
            # Convert time difference to days and normalize
            days_old = (current_time - pub_date).days
            recency_score = 1 / (1 + days_old)  # Newer articles get higher scores
        except (ValueError, TypeError, AttributeError):
            recency_score = 0
        recency_scores.append(recency_score)
    
    # Normalize scores
    recency_scores = np.array(recency_scores)
    recency_scores = recency_scores / recency_scores.max() if recency_scores.max() > 0 else recency_scores
    
    # Combine relevance and recency scores (0.7 weight for relevance, 0.3 for recency)
    final_scores = 0.7 * similarity_scores + 0.3 * recency_scores
    
    # Get indices of top N articles
    top_indices = final_scores.argsort()[-top_n:][::-1]
    
    # Return top articles with their scores
    top_articles = []
    for idx in top_indices:
        article = articles[idx].copy()
        article['relevance_score'] = float(final_scores[idx])
        top_articles.append(article)
    
    return top_articles

def format_mailchimp_content(articles: List[Dict]) -> str:
    """Format the top articles into Mailchimp-compatible HTML format.
    
    Args:
        articles: List of article dictionaries containing title and URL
        
    Returns:
        str: HTML formatted content for Mailchimp
    """
    html = '''
    <h2 style="color: #333333; font-family: 'Arial', sans-serif; font-size: 24px; 
               margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #dddddd;">
        Senior Living Headlines
    </h2>
    <ul style="list-style-type: none; padding: 0; margin: 0;">
    '''
    
    for article in articles:
        title = article['title']
        url = article['url']
        html += f'''
        <li style="margin-bottom: 15px;">
            <a href="{url}" style="color: #0066cc; text-decoration: none; 
                      font-family: 'Arial', sans-serif; font-size: 16px;">
                {title}
            </a>
        </li>
        '''
    
    html += '\n    </ul>'
    return html

def send_to_mailchimp(content: str, api_key: str = None, list_id: str = None) -> Dict:
    """Send formatted content to Mailchimp API.
    
    Args:
        content: HTML formatted content
        api_key: Mailchimp API key (defaults to environment variable)
        list_id: Mailchimp audience list ID (defaults to environment variable)
        
    Returns:
        Dict: API response
    """
    if not api_key:
        api_key = os.getenv('MAILCHIMP_API_KEY')
        if not api_key:
            raise ValueError("Mailchimp API key not found. Set MAILCHIMP_API_KEY environment variable.")
    
    if not list_id:
        list_id = os.getenv('MAILCHIMP_LIST_ID')
        if not list_id:
            raise ValueError("Mailchimp list ID not found. Set MAILCHIMP_LIST_ID environment variable.")
    
    # Initialize the Mailchimp client
    client = MailChimp(mc_api=api_key)
    
    # Create a campaign
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
    
    # Set the campaign content
    client.campaigns.content.update(campaign_info['id'], {
        'html': content
    })
    
    return campaign_info

def main():
    # Load articles
    articles = load_articles('output.json')
    
    # Rank and select top articles
    top_articles = rank_articles(articles)
    
    '''
    # Format content for Mailchimp
    mailchimp_content = format_mailchimp_content(top_articles)
    
    # Save formatted content locally (for review)
    with open('newsletter_content.html', 'w') as f:
        f.write(mailchimp_content)
    
    # Send to Mailchimp
    try:
        response = send_to_mailchimp(mailchimp_content)
        print(f"Campaign successfully created in Mailchimp! Campaign ID: {response.get('id')}")
        print("Note: The campaign is created as a draft. Log into Mailchimp to review and send.")
    except Exception as e:
        print(f"Error sending to Mailchimp: {str(e)}")
    
    print("Newsletter content has been generated! Check newsletter_content.html")
    '''
if __name__ == "__main__":
    main()

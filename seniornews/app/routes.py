from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app import db
from app.models import Article
from app.services import scrape_articles, select_top_articles, send_newsletter, format_articles_html

bp = Blueprint('main', __name__)

@bp.route('/api/scrape', methods=['POST'])
def scrape():
    """Trigger article scraping"""
    try:
        articles = scrape_articles()
        return jsonify({
            'message': f'Successfully scraped {len(articles)} articles',
            'articles': [article.to_dict() for article in articles]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/articles', methods=['GET'])
def get_articles():
    """Get all articles"""
    articles = Article.query.order_by(Article.publication_date.desc()).all()
    return jsonify([article.to_dict() for article in articles])

@bp.route('/api/select-articles', methods=['POST'])
def select_articles():
    """Select top articles and prepare newsletter"""
    try:
        selected_articles = select_top_articles()
        return jsonify({
            'message': 'Successfully selected top articles',
            'articles': [article.to_dict() for article in selected_articles]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500  

@bp.route('/api/send-newsletter', methods=['POST'])
def create_newsletter():
    """Create and send newsletter"""
    try:
        result = send_newsletter()
        return jsonify({
            'message': 'Newsletter created successfully',
            'campaign_id': result.get('id')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/senior-housing/headlines', methods=['GET', 'POST'])
def get_senior_housing_headlines():
    """Get or refresh Senior Housing News headlines within a date range"""
    num_headlines = request.args.get('num_headlines', default=5, type=int)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    
    try:
        if request.method == 'POST':
            # If POST, scrape new articles
            articles = scrape_articles(start_date=start_date, end_date=end_date)
            print(articles)
            if not articles:
                return jsonify({'error': 'No new articles found. Please try again later.'}), 404
        else:
            # If GET, use existing articles
            if start_date and end_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                articles = Article.query.filter(
                    Article.publication_date >= start_datetime,
                    Article.publication_date <= end_datetime
                ).order_by(Article.publication_date.desc()).all()
            else:
                articles = Article.query.order_by(Article.publication_date.desc()).all()
                
            if not articles:
                articles = scrape_articles(start_date=start_date, end_date=end_date)
                if not articles:
                    return jsonify({'error': 'No articles available. Please try regenerating headlines.'}), 404
        
        # Select and sort top articles
        try:
            top_articles = select_top_articles(articles, limit=num_headlines)
            if not top_articles:
                return jsonify({'error': 'Failed to select top articles'}), 500
        except Exception as e:
            print(f'Error selecting top articles: {str(e)}')
            return jsonify({'error': 'Failed to process articles'}), 500
        
        # Format HTML content
        try:
            html_content = format_articles_html(top_articles)
        except Exception as e:
            print(f'Error formatting HTML: {str(e)}')
            return jsonify({'error': 'Failed to format articles'}), 500
        
        # Convert articles to dict format
        article_dicts = [article.to_dict() for article in top_articles]
        
        response_data = {
            'articles': article_dicts,
            'html_content': html_content
        }
        
        # Debug logging
        print('Response data:', response_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f'Error in get_senior_housing_headlines: {str(e)}')
        return jsonify({'error': str(e)}), 500

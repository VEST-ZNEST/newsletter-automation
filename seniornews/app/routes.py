from flask import Blueprint, jsonify, request
from app import db
from app.models import Article
from app.services import scrape_articles, select_top_articles, send_newsletter

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

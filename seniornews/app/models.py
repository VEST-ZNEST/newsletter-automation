from datetime import datetime
from app import db

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(100))
    publication_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    relevance_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_selected = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'author': self.author,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'relevance_score': self.relevance_score,
            'is_selected': self.is_selected
        }

    @staticmethod
    def from_scrapy_item(item):
        return Article(
            title=item['title'],
            url=item['url'],
            author=item.get('author'),
            publication_date=datetime.fromisoformat(item['publication_date'].replace('Z', '+00:00'))
            if 'publication_date' in item else None
        )

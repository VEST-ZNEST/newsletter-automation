"""Remove duplicates and add URL constraint

Revision ID: 3ed134c78f34
Revises: dbee0ee5330c
Create Date: 2025-03-04 14:30:04.279461

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ed134c78f34'
down_revision = 'dbee0ee5330c'
branch_labels = None
depends_on = None


from sqlalchemy import text

def upgrade():
    # Create a new table with unique constraint
    op.execute("""
        CREATE TABLE article_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(500) NOT NULL,
            url VARCHAR(500) NOT NULL UNIQUE,
            author VARCHAR(100),
            publication_date DATETIME NOT NULL,
            relevance_score FLOAT,
            created_at DATETIME NOT NULL,
            is_selected BOOLEAN
        );
    """)
    
    # Copy data, keeping only the latest version of each article
    op.execute("""
        INSERT INTO article_new (title, url, author, publication_date, relevance_score, created_at, is_selected)
        SELECT title, url, author, publication_date, relevance_score, created_at, is_selected
        FROM article
        GROUP BY url
        HAVING publication_date = MAX(publication_date);
    """)
    
    # Drop old table and rename new one
    op.execute("DROP TABLE article;")
    op.execute("ALTER TABLE article_new RENAME TO article;")


def downgrade():
    # Remove unique constraint
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.drop_constraint('uq_article_url', type_='unique')

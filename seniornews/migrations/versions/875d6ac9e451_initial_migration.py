"""initial migration

Revision ID: 875d6ac9e451
Revises: 
Create Date: 2025-03-05 23:40:42.995971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '875d6ac9e451'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.Column('author', sa.String(length=100), nullable=True),
    sa.Column('publication_date', sa.DateTime(), nullable=False),
    sa.Column('relevance_score', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_selected', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url', name='uq_article_url')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('article')
    # ### end Alembic commands ###

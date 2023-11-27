"""add_field is_active to price

Revision ID: cacb2bf3b505
Revises: 92c5a2b0ac6c
Create Date: 2023-11-27 21:30:23.288671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cacb2bf3b505'
down_revision = '92c5a2b0ac6c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('prices', sa.Column('is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('prices', 'is_active')
    # ### end Alembic commands ###

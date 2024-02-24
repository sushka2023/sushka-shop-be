"""changed option nullable of price order fields

Revision ID: e002bab14e1f
Revises: 5c187d5a55d5
Create Date: 2024-02-11 10:44:40.830131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e002bab14e1f'
down_revision = '5c187d5a55d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'price_order',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'price_order',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
    # ### end Alembic commands ###
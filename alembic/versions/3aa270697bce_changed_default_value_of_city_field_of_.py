"""changed default value of city field of orders table

Revision ID: 3aa270697bce
Revises: 247ea90218c0
Create Date: 2024-01-18 15:52:40.427013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3aa270697bce'
down_revision = '247ea90218c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'city',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'city',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    # ### end Alembic commands ###
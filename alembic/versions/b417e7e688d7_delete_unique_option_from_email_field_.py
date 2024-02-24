"""delete unique option from email field of orders table

Revision ID: b417e7e688d7
Revises: 39e2c779f7d3
Create Date: 2024-02-24 11:09:59.774056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b417e7e688d7'
down_revision = '39e2c779f7d3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('orders_email_anon_user_key', 'orders', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('orders_email_anon_user_key', 'orders', ['email_anon_user'])
    # ### end Alembic commands ###
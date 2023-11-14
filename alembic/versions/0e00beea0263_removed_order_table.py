"""removed order table

Revision ID: 0e00beea0263
Revises: 5369f42c21ba
Create Date: 2023-11-13 20:14:25.278740

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0e00beea0263'
down_revision = '5369f42c21ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('basket_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('price_order', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('payment_type', postgresql.ENUM('cash_on_delivery_np', 'liqpay', name='paymenttype'), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('confirmation_manager', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('confirmation_pay', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('call_manager', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['basket_id'], ['baskets.id'], name='orders_basket_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='orders_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='orders_pkey')
    )
    # ### end Alembic commands ###
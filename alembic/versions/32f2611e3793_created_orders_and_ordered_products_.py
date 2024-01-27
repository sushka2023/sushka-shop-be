"""created orders and ordered_products tables

Revision ID: 32f2611e3793
Revises: e54baee698b7
Create Date: 2024-01-27 17:03:23.747074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32f2611e3793'
down_revision = 'e54baee698b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('basket_id', sa.Integer(), nullable=True),
    sa.Column('price_order', sa.Float(), nullable=False),
    sa.Column('payment_type', sa.Enum('cash_on_delivery_np', 'liqpay', name='paymentstypes'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('confirmation_manager', sa.Boolean(), nullable=True),
    sa.Column('confirmation_pay', sa.Boolean(), nullable=True),
    sa.Column('call_manager', sa.Boolean(), nullable=True),
    sa.Column('status_order', sa.Enum('new', 'in_processing', 'shipped', 'delivered', 'cancelled', name='ordersstatus'), nullable=True),
    sa.Column('post_type', sa.Enum('nova_poshta_warehouse', 'nova_poshta_address', 'ukr_poshta', name='posttype'), nullable=True),
    sa.Column('address_warehouse', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=255), nullable=True),
    sa.Column('region', sa.String(length=255), nullable=True),
    sa.Column('area', sa.String(length=255), nullable=True),
    sa.Column('street', sa.String(length=255), nullable=True),
    sa.Column('house_number', sa.String(length=255), nullable=True),
    sa.Column('apartment_number', sa.String(length=255), nullable=True),
    sa.Column('floor', sa.Integer(), nullable=True),
    sa.Column('country', sa.String(length=255), nullable=True),
    sa.Column('post_code', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['basket_id'], ['baskets.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ordered_products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('price_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['price_id'], ['prices.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ordered_products')
    op.drop_table('orders')
    # ### end Alembic commands ###
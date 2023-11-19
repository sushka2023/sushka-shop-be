"""create order table

Revision ID: d0171fafb624
Revises: a1592e8d6968
Create Date: 2023-11-14 23:25:10.662258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0171fafb624'
down_revision = 'a1592e8d6968'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('basket_id', sa.Integer(), nullable=True),
                    sa.Column('price_order', sa.Float(), nullable=False),
                    sa.Column('payment_type', sa.Enum('cash_on_delivery_np', 'liqpay', name='paymenttypes'), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('confirmation_manager', sa.Boolean(), nullable=True),
                    sa.Column('confirmation_pay', sa.Boolean(), nullable=True),
                    sa.Column('call_manager', sa.Boolean(), nullable=True),
                    sa.Column('status_order', sa.Enum('new', 'in_processing', 'shipped', 'delivered', 'cancelled', name='orderstatus'), nullable=True),
                    sa.ForeignKeyConstraint(['basket_id'], ['baskets.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    # ### end Alembic commands ###

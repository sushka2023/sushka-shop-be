"""product and product category

Revision ID: 0765abaf2581
Revises: e44bdb15b6de
Create Date: 2023-07-07 23:17:46.598980

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0765abaf2581'
down_revision = 'e44bdb15b6de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('product_categories_product_id_fkey', 'product_categories', type_='foreignkey')
    op.drop_column('product_categories', 'product_id')
    op.add_column('products', sa.Column('product_category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'products', 'product_categories', ['product_category_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'products', type_='foreignkey')
    op.drop_column('products', 'product_category_id')
    op.add_column('product_categories', sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('product_categories_product_id_fkey', 'product_categories', 'products', ['product_id'], ['id'])
    # ### end Alembic commands ###

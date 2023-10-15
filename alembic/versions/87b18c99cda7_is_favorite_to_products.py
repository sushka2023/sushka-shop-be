"""is_favorite_to_products

Revision ID: 87b18c99cda7
Revises: 926100626ef8
Create Date: 2023-10-07 18:23:37.894220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87b18c99cda7'
down_revision = '926100626ef8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('is_favorite', sa.Boolean(), nullable=True))
    op.alter_column('products', 'description',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=400),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'description',
               existing_type=sa.String(length=400),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)
    op.drop_column('products', 'is_favorite')
    # ### end Alembic commands ###
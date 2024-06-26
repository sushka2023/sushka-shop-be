"""added category_warehouse field to nova_poshta table

Revision ID: e174f9c90007
Revises: 40df38905f41
Create Date: 2024-06-04 19:17:35.060543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e174f9c90007'
down_revision = '40df38905f41'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('nova_poshta', sa.Column('category_warehouse', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('nova_poshta', 'category_warehouse')
    # ### end Alembic commands ###

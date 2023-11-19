"""added product status

Revision ID: 92c5a2b0ac6c
Revises: ec99fb476df2
Create Date: 2023-11-14 22:51:33.466070

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92c5a2b0ac6c'
down_revision = 'ec99fb476df2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE TYPE productstatus AS ENUM('new', 'activated', 'archived')")
    op.add_column('products',
                  sa.Column('product_status',
                            sa.Enum('new', 'activated', 'archived', name='productstatus'), nullable=True, default='new'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'product_status')
    op.execute("DROP TYPE productstatus")
    # ### end Alembic commands ###
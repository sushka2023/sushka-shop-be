"""changed type of rate field

Revision ID: 55c867d5bded
Revises: 7b510eefe8e2
Create Date: 2023-10-29 22:08:03.939234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55c867d5bded'
down_revision = '7b510eefe8e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE reviews ALTER COLUMN rate TYPE rate USING rate::text::rate;")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE reviews ALTER COLUMN rate TYPE text USING rate::text;")
    # ### end Alembic commands ###

"""added enum to rate field

Revision ID: 09007ede6a12
Revises: 55c867d5bded
Create Date: 2023-10-29 22:44:35.423283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09007ede6a12'
down_revision = '55c867d5bded'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE reviews ALTER COLUMN rate TYPE text;")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE reviews ALTER COLUMN rate TYPE integer;")
    # ### end Alembic commands ###
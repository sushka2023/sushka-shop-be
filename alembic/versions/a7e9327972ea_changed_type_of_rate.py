"""changed type of rate

Revision ID: a7e9327972ea
Revises: 8b039d7f2fb9
Create Date: 2023-10-29 23:12:36.668424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7e9327972ea'
down_revision = '8b039d7f2fb9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('reviews', 'rate',
                    existing_type=sa.TEXT(),
                    type_=sa.Enum('one_star', 'two_stars', 'three_stars', 'four_stars', 'five_stars', name='rate'),
                    existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('reviews', 'rate',
                    existing_type=sa.Enum('one_star', 'two_stars', 'three_stars', 'four_stars', 'five_stars', name='rate'),
                    type_=sa.TEXT(),
                    existing_nullable=True)
    # ### end Alembic commands ###

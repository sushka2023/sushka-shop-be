"""merge message

Revision ID: 0f7e636a83e8
Revises: cacb2bf3b505, b270a60b7522
Create Date: 2023-12-15 23:15:20.603687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f7e636a83e8'
down_revision = ('cacb2bf3b505', 'b270a60b7522')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""Init db. Create user and role

Revision ID: ad6cf9b1478a
Revises: 
Create Date: 2023-07-01 14:22:01.403983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad6cf9b1478a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('roles', sa.Enum('admin', 'moderator', 'user', name='role'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('first_name', sa.String(length=150), nullable=False),
    sa.Column('last_name', sa.String(length=150), nullable=False),
    sa.Column('patroymic', sa.String(length=150), nullable=True),
    sa.Column('phone_number', sa.String(length=50), nullable=True),
    sa.Column('password_checksum', sa.String(length=255), nullable=False),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('is_blocked', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.execute("DROP TYPE role")
    # ### end Alembic commands ###

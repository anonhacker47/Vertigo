"""add mal id to series

Revision ID: e5f1b7c3d9a2
Revises: d4e9a1b6c2f7
Create Date: 2026-11-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5f1b7c3d9a2'
down_revision = 'd4e9a1b6c2f7'
branch_labels = None
depends_on = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()


def upgrade_() -> None:
    with op.batch_alter_table('series', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mal_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('mal_url', sa.String(length=280), nullable=True))


def downgrade_() -> None:
    with op.batch_alter_table('series', schema=None) as batch_op:
        batch_op.drop_column('mal_url')
        batch_op.drop_column('mal_id')

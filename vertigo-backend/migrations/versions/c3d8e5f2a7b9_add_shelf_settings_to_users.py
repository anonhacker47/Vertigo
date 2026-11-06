"""add shelf settings to users

Revision ID: c3d8e5f2a7b9
Revises: b2c7d4e9f1a3
Create Date: 2026-11-06 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d8e5f2a7b9'
down_revision = 'b2c7d4e9f1a3'
branch_labels = None
depends_on = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()


def upgrade_() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shelf_settings', sa.JSON(), nullable=True))


def downgrade_() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('shelf_settings')

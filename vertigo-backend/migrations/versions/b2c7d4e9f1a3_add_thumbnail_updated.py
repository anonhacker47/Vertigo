"""add thumbnail_updated to series, issues and entities

Revision ID: b2c7d4e9f1a3
Revises: a4f1c9d27b58
Create Date: 2026-11-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c7d4e9f1a3'
down_revision = 'a4f1c9d27b58'
branch_labels = None
depends_on = None

TABLES = ('series', 'issue', 'publisher', 'creator', 'character')


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()


def upgrade_() -> None:
    for table in TABLES:
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.add_column(sa.Column('thumbnail_updated', sa.DateTime(), nullable=True))
        # Backfill so existing cover URLs do not change.
        op.execute(sa.text(
            f"UPDATE {table} SET thumbnail_updated = last_updated "
            f"WHERE thumbnail IS NOT NULL AND thumbnail != ''"
        ))


def downgrade_() -> None:
    for table in TABLES:
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.drop_column('thumbnail_updated')

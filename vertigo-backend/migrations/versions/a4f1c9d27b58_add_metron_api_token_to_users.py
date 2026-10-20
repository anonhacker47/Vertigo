"""add metron api token to users

Revision ID: a4f1c9d27b58
Revises: e1b833753b38
Create Date: 2026-10-20 13:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4f1c9d27b58'
down_revision = 'e1b833753b38'
branch_labels = None
depends_on = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()





def upgrade_() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('metron_api_token', sa.String(length=255), nullable=True))


def downgrade_() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('metron_api_token')

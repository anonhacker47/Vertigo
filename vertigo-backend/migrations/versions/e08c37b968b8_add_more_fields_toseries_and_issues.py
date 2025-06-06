"""add more fields toseries and issues

Revision ID: e08c37b968b8
Revises: e232f3f495c9
Create Date: 2024-03-26 14:51:31.859132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e08c37b968b8'
down_revision = 'e232f3f495c9'
branch_labels = None
depends_on = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()





def upgrade_() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('issue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('number', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('summary', sa.String(length=570), nullable=True))
        batch_op.add_column(sa.Column('bought_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('read_date', sa.DateTime(), nullable=True))

    with op.batch_alter_table('series', schema=None) as batch_op:
        batch_op.add_column(sa.Column('inker', sa.String(length=280), nullable=True))
        batch_op.add_column(sa.Column('penciller', sa.String(length=280), nullable=True))
        batch_op.add_column(sa.Column('colorist', sa.String(length=280), nullable=True))
        batch_op.add_column(sa.Column('letterer', sa.String(length=280), nullable=True))
        batch_op.add_column(sa.Column('characters', sa.String(length=570), nullable=True))
        batch_op.add_column(sa.Column('teams', sa.String(length=570), nullable=True))
        batch_op.add_column(sa.Column('user_rating', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('manga', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('release_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('issue_count', sa.Integer(), nullable=True))
        batch_op.drop_column('books_count')

    # ### end Alembic commands ###


def downgrade_() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('series', schema=None) as batch_op:
        batch_op.add_column(sa.Column('books_count', sa.INTEGER(), nullable=True))
        batch_op.drop_column('issue_count')
        batch_op.drop_column('release_date')
        batch_op.drop_column('manga')
        batch_op.drop_column('user_rating')
        batch_op.drop_column('teams')
        batch_op.drop_column('characters')
        batch_op.drop_column('letterer')
        batch_op.drop_column('colorist')
        batch_op.drop_column('penciller')
        batch_op.drop_column('inker')

    with op.batch_alter_table('issue', schema=None) as batch_op:
        batch_op.drop_column('read_date')
        batch_op.drop_column('bought_date')
        batch_op.drop_column('summary')
        batch_op.drop_column('number')

    # ### end Alembic commands ###
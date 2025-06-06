"""updates tables

Revision ID: a61737a812d1
Revises: 22a968057e40
Create Date: 2024-07-16 17:29:18.557852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a61737a812d1'
down_revision = '22a968057e40'
branch_labels = None
depends_on = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()





def upgrade_() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('publisher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=280), nullable=False),
    sa.Column('description', sa.String(length=1250), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('publisher', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_publisher_timestamp'), ['timestamp'], unique=False)

    op.create_table('series_publisher',
    sa.Column('series_id', sa.Integer(), nullable=False),
    sa.Column('publisher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['publisher_id'], ['publisher.id'], ),
    sa.ForeignKeyConstraint(['series_id'], ['series.id'], ),
    sa.PrimaryKeyConstraint('series_id', 'publisher_id')
    )
    with op.batch_alter_table('series', schema=None) as batch_op:
        batch_op.add_column(sa.Column('main_char_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('main_char_type', sa.String(length=50), nullable=True))
        batch_op.drop_column('publisher')
        batch_op.drop_column('main_char')

    # ### end Alembic commands ###


def downgrade_() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('series', schema=None) as batch_op:
        batch_op.add_column(sa.Column('main_char', sa.VARCHAR(length=280), nullable=True))
        batch_op.add_column(sa.Column('publisher', sa.VARCHAR(length=280), nullable=True))
        batch_op.drop_column('main_char_type')
        batch_op.drop_column('main_char_id')

    op.drop_table('series_publisher')
    with op.batch_alter_table('publisher', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_publisher_timestamp'))

    op.drop_table('publisher')
    # ### end Alembic commands ###


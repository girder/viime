"""
empty message

Revision ID: de010dc14402
Revises: 55365e50ff52
Create Date: 2020-07-02 14:17:23.420116

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'de010dc14402'
down_revision = '55365e50ff52'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('csv_file', sa.Column('column_json', sqlalchemy_utils.types.json.JSONType(), nullable=False))
    op.add_column('csv_file', sa.Column('row_json', sqlalchemy_utils.types.json.JSONType(), nullable=False))

    # move row/column information into csv_file table here:

    op.drop_table('table_row')
    op.drop_table('table_column')


def downgrade():
    op.drop_column('csv_file', 'row_json')
    op.drop_column('csv_file', 'column_json')
    op.create_table(
        'table_column',
        sa.Column('csv_file_id', sa.CHAR(length=32), nullable=False),
        sa.Column('column_index', sa.INTEGER(), nullable=False),
        sa.Column('column_type', sa.VARCHAR(), nullable=False),
        sa.Column('meta', sa.TEXT(), nullable=True),
        sa.Column('subtype', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['csv_file_id'], ['csv_file.id'], name='fk_table_column_csv_file_id_csv_file'),
        sa.PrimaryKeyConstraint('csv_file_id', 'column_index', name='pk_table_column')
    )
    op.create_table(
        'table_row',
        sa.Column('csv_file_id', sa.CHAR(length=32), nullable=False),
        sa.Column('row_index', sa.INTEGER(), nullable=False),
        sa.Column('row_type', sa.VARCHAR(), nullable=False),
        sa.Column('meta', sa.TEXT(), nullable=True),
        sa.Column('subtype', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['csv_file_id'], ['csv_file.id'], name='fk_table_row_csv_file_id_csv_file'),
        sa.PrimaryKeyConstraint('csv_file_id', 'row_index', name='pk_table_row')
    )

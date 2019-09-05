"""
refactor csv file model

Revision ID: 543488f52e75
Revises: 44b9d38a1bb9
Create Date: 2019-09-05 10:08:04.700364

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

from metabulo.models import CSVFile, db, ValidatedMetaboliteTable


revision = '543488f52e75'
down_revision = '44b9d38a1bb9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'validated_metabolite_table',
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('csv_file_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('normalization', sa.String(), nullable=True),
        sa.Column('normalization_argument', sa.String(), nullable=True),
        sa.Column('transformation', sa.String(), nullable=True),
        sa.Column('scaling', sa.String(), nullable=True),
        sa.Column('meta', sqlalchemy_utils.types.json.JSONType(), nullable=False),
        sa.Column('raw_measurements_bytes', sa.LargeBinary(), nullable=False),
        sa.Column('measurement_metadata_bytes', sa.LargeBinary(), nullable=False),
        sa.Column('sample_metadata_bytes', sa.LargeBinary(), nullable=False),
        sa.Column('groups_bytes', sa.LargeBinary(), nullable=False),
        sa.ForeignKeyConstraint(
            ['csv_file_id'], ['csv_file.id'],
            name=op.f('fk_validated_metabolite_table_csv_file_id_csv_file')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_validated_metabolite_table'))
    )
    op.create_index(
        op.f('ix_validated_metabolite_table_csv_file_id'),
        'validated_metabolite_table', ['csv_file_id'], unique=True)

    # sqlite doesn't support this operation:
    # op.drop_column('csv_file', 'scaling')
    # op.drop_column('csv_file', 'normalization_argument')
    # op.drop_column('csv_file', 'transformation')
    # op.drop_column('csv_file', 'normalization')

    op.execute('ALTER TABLE csv_file RENAME TO csv_file_old;')
    op.create_table(
        'csv_file',
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('imputation_mnar', sa.String(), nullable=False),
        sa.Column('imputation_mcar', sa.String(), nullable=False),
        sa.Column('meta', sqlalchemy_utils.types.json.JSONType(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_csv_file'))
    )

    op.execute("""
        INSERT INTO csv_file
        SELECT
            id, created, name, imputation_mnar, imputation_mcar, meta
        FROM
            csv_file_old;
    """)
    op.execute('DROP TABLE csv_file_old;')

    for csv_file in CSVFile.query:
        try:
            validated_table = ValidatedMetaboliteTable.create_from_csv_file(csv_file)
        except Exception:
            continue

        db.session.add(validated_table)

    db.session.commit()


def downgrade():
    op.add_column('csv_file', sa.Column('normalization', sa.VARCHAR(), nullable=True))
    op.add_column('csv_file', sa.Column('transformation', sa.VARCHAR(), nullable=True))
    op.add_column('csv_file', sa.Column('normalization_argument', sa.VARCHAR(), nullable=True))
    op.add_column('csv_file', sa.Column('scaling', sa.VARCHAR(), nullable=True))
    op.drop_index(
        op.f('ix_validated_metabolite_table_csv_file_id'), table_name='validated_metabolite_table')
    op.drop_table('validated_metabolite_table')

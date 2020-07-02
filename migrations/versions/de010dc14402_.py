"""
empty message

Revision ID: de010dc14402
Revises: 55365e50ff52
Create Date: 2020-07-02 14:17:23.420116

"""
from alembic import op
from marshmallow import fields, validate
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.uuid import UUIDType

from viime.models import BaseModel, BaseSchema, CSVFile, db, \
    METADATA_TYPES, TABLE_COLUMN_TYPES, TABLE_ROW_TYPES, \
    ValidatedMetaboliteTable


# revision identifiers, used by Alembic.
revision = 'de010dc14402'
down_revision = '55365e50ff52'
branch_labels = None
depends_on = None


class TableColumn(BaseModel):
    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    column_index = db.Column(db.Integer, primary_key=True)
    column_type = db.Column(db.String, nullable=False)
    subtype = db.Column(db.String, nullable=True)
    meta = db.Column(JSONType, nullable=True)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('columns', lazy=True, order_by='TableColumn.column_index'))


class TableColumnSchema(BaseSchema):
    __model__ = TableColumn  # type: ignore

    column_index = fields.Int(required=True, validate=validate.Range(min=0))
    column_type = fields.Str(required=True, validate=validate.OneOf(TABLE_COLUMN_TYPES))
    subtype = fields.Str(required=False, validate=validate.OneOf(METADATA_TYPES))
    meta = fields.Dict(missing=dict)


class TableRow(BaseModel):
    csv_file_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    row_index = db.Column(db.Integer, primary_key=True)
    row_type = db.Column(db.String, nullable=False)
    subtype = db.Column(db.String, nullable=True)
    meta = db.Column(JSONType, nullable=True)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('rows', lazy=True, order_by='TableRow.row_index'))


class TableRowSchema(BaseSchema):
    __model__ = TableRow  # type: ignore

    row_name = fields.Str(dump_only=True)
    row_index = fields.Int(required=True, validate=validate.Range(min=0))
    row_type = fields.Str(required=True, validate=validate.OneOf(TABLE_ROW_TYPES))
    subtype = fields.Str(required=False, validate=validate.OneOf(METADATA_TYPES))
    meta = fields.Dict(missing=dict)


def upgrade():  # noqa
    column_schema = TableColumnSchema()
    row_schema = TableRowSchema()
    op.add_column(
        'csv_file',
        sa.Column('column_json', sqlalchemy_utils.types.json.JSONType(), nullable=True)
    )
    op.add_column(
        'csv_file',
        sa.Column('row_json', sqlalchemy_utils.types.json.JSONType(), nullable=True)
    )

    # move row/column information into csv_file table here:
    for csv_file in CSVFile.query:
        try:
            column_json = column_schema.dump(csv_file.columns, many=True)
            row_json = row_schema.dump(csv_file.rows, many=True)

            key_column_index = 0
            data_column_index = 0
            for index, column in enumerate(column_json):
                dci = None
                if column['column_type'] == TABLE_COLUMN_TYPES.DATA:
                    dci = data_column_index
                    data_column_index += 1
                elif column['column_type'] == TABLE_COLUMN_TYPES.INDEX:
                    key_column_index = index
                column['data_column_index'] = dci

            header_row_index = 0
            data_row_index = 0
            keys = csv_file.table.iloc[:, key_column_index]
            for index, row in enumerate(row_json):
                dri = None
                if row['row_type'] == TABLE_ROW_TYPES.DATA:
                    dri = data_row_index
                    data_row_index += 1
                elif row['row_type'] == TABLE_ROW_TYPES.INDEX:
                    header_row_index = index

                row['data_row_index'] = dri
                row['row_name'] = str(keys.iloc[index])

            headers = csv_file.table.iloc[header_row_index, :]
            for index, column in enumerate(column_json):
                column['column_header'] = str(headers.iloc[index])

            csv_file.column_json = column_json
            csv_file.row_json = row_json
        except Exception:
            # some tables have irreconcileable errors, so just delete them
            print(f'Deleting {csv_file.id}')
            for row in csv_file.rows:
                db.session.delete(row)
            for column in csv_file.columns:
                db.session.delete(column)
            validated = ValidatedMetaboliteTable.query.filter_by(csv_file_id=csv_file.id).first()
            if validated:
                db.session.delete(validated)
            db.session.commit()
            db.session.delete(csv_file)

        db.session.commit()

    with op.batch_alter_table('csv_file', schema=None) as batch_op:
        batch_op.alter_column('column_json', nullable=False)
        batch_op.alter_column('row_json', nullable=False)
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
        sa.ForeignKeyConstraint(
            ['csv_file_id'], ['csv_file.id'],
            name='fk_table_column_csv_file_id_csv_file'
        ),
        sa.PrimaryKeyConstraint('csv_file_id', 'column_index', name='pk_table_column')
    )
    op.create_table(
        'table_row',
        sa.Column('csv_file_id', sa.CHAR(length=32), nullable=False),
        sa.Column('row_index', sa.INTEGER(), nullable=False),
        sa.Column('row_type', sa.VARCHAR(), nullable=False),
        sa.Column('meta', sa.TEXT(), nullable=True),
        sa.Column('subtype', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(
            ['csv_file_id'], ['csv_file.id'], name='fk_table_row_csv_file_id_csv_file'),
        sa.PrimaryKeyConstraint('csv_file_id', 'row_index', name='pk_table_row')
    )

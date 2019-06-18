from sqlalchemy.event import listen, listens_for
from sqlalchemy.orm.attributes import get_history

from metabulo.cache import clear_cache
from metabulo.models import CSVFile, db, TABLE_COLUMN_TYPES, TABLE_ROW_TYPES, \
    TableColumn, TableRow

listen(CSVFile, 'after_update', lambda mapper, connection, target: clear_cache(csv_file=target))
listen(TableRow, 'after_update',
       lambda mapper, connection, target: clear_cache(csv_file=target.csv_file))
listen(TableColumn, 'after_update',
       lambda mapper, connection, target: clear_cache(csv_file=target.csv_file))


def has_changed(entity, column):
    return not get_history(entity, column)[1]


def get_change(entity, column):
    new, unchanged, old = get_history(entity, column)
    if unchanged:
        return unchanged, unchanged
    else:
        return old, new


def set_row_names_from_column(column):
    csv = column.csv_file.table
    rows = TableRow.query.filter_by(
        csv_file_id=column.csv_file_id
    )
    for row in rows:
        row.row_name = csv.iloc[row.row_index, column.column_index]
        db.session.add(row)


def set_column_names_from_row(row):
    csv = row.csv_file.table
    columns = TableColumn.query.filter_by(
        csv_file_id=row.csv_file_id
    )
    for column in columns:
        column.column_header = csv.iloc[row.row_index, column.column_index]
        db.session.add(column)


def set_data_row_indices(rows):
    index = 0
    for r in rows:
        if r.row_type == TABLE_ROW_TYPES.DATA:
            r.data_row_index = index
            index += 1
            db.session.add(r)


def set_data_column_indices(columns):
    index = 0
    for c in columns:
        if c.column_type == TABLE_COLUMN_TYPES.DATA:
            c.data_column_index = index
            index += 1
            db.session.add(c)


def after_create_csv_file(csv_file):
    # It would be nice for this to be an ORM event, but I'm not
    # sure how to make it fire *after* the rows/columns have been
    # added.  For now, we trigger it manually on create.
    set_row_names_from_column(csv_file.key_column)
    set_column_names_from_row(csv_file.header_row)
    set_data_row_indices(csv_file.rows)
    set_data_column_indices(csv_file.columns)


@listens_for(TableColumn, 'after_update')
def set_data_column_index(mapper, connection, column):
    old, new = get_change(column, 'column_type')
    if old == new or TABLE_COLUMN_TYPES.DATA not in (old, new):
        return

    columns = TableColumn.query.filter_by(
        csv_file_id=column.csv_file_id
    ).order_by(
        TableColumn.column_index
    )
    set_data_column_indices(columns)


@listens_for(TableRow, 'after_update')
def set_data_row_index(mapp, connection, row):
    old, new = get_change(row, 'row_type')
    if old == new or TABLE_COLUMN_TYPES.DATA not in (old, new):
        return

    rows = TableRow.query.filter_by(
        csv_file_id=row.csv_file_id
    ).order_by(
        TableRow.row_index
    )
    set_data_row_indices(rows)


@listens_for(TableColumn, 'after_update')
def change_key_column(mapper, connection, column):
    if not has_changed(column, 'column_type'):
        return

    if column.column_type == TABLE_COLUMN_TYPES.INDEX:
        set_row_names_from_column(column)


@listens_for(TableRow, 'after_update')
def change_key_row(mapper, connection, row):
    if not has_changed(row, 'row_type'):
        return

    if row.row_type == TABLE_ROW_TYPES.INDEX:
        set_column_names_from_row(row)

"""
This module contains methods related to mergind dataset
"""
from typing import List

import pandas

from viime.models import TABLE_COLUMN_TYPES, TABLE_ROW_TYPES, \
    ValidatedMetaboliteTable


def simple_merge(validated_tables: List[ValidatedMetaboliteTable]):
    """
    Generate a new validated csv file by concatonating a list of 2 or more
    validated tables.

    NOTE: This current uses the groups from the first table, removes
    all of the metadata, and does and "inner join" with the row indices
    """

    tables: List[pandas.DataFrame] = []
    column_types: List[str] = [
        TABLE_COLUMN_TYPES.INDEX
    ]
    measurement_metadata: List[str] = []

    to_merge = [
        (TABLE_COLUMN_TYPES.GROUP, 'groups'),
        (TABLE_COLUMN_TYPES.METADATA, 'sample_metadata'),
        (TABLE_COLUMN_TYPES.DATA, 'measurements')
    ]
    for (column_type, attr) in to_merge:
        for table in validated_tables:
            df = getattr(table, attr)
            count = df.shape[1]
            print(count, table.csv_file_id, column_type)
            tables.append(df)
            column_types.extend([column_type] * count)
            measurement_metadata.extend([str(table.csv_file_id)] * count)

    merged = pandas.concat(tables, axis=1, join='inner')

    # create similar structure
    metadata = pandas.DataFrame(measurement_metadata).T
    metadata.columns = list(merged)

    row_types = [
        TABLE_ROW_TYPES.INDEX,
        TABLE_ROW_TYPES.METADATA  # data source
    ] + ([TABLE_ROW_TYPES.DATA] * merged.shape[0])

    # merge as str
    table = pandas.concat([metadata, merged.astype(str)])

    return table.to_csv(), column_types, row_types

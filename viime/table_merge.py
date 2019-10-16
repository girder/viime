"""
This module contains methods related to mergind dataset
"""
from typing import Dict, List, Set

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

    used_column_names: Set[str] = set()
    tables: List[pandas.DataFrame] = []
    column_types: List[str] = [
        TABLE_COLUMN_TYPES.INDEX
    ]
    measurement_metadata: List[int] = []

    to_merge = [
        (TABLE_COLUMN_TYPES.GROUP, 'groups'),
        (TABLE_COLUMN_TYPES.METADATA, 'sample_metadata'),
        (TABLE_COLUMN_TYPES.DATA, 'measurements')
    ]
    for (column_type, attr) in to_merge:
        for index, table in enumerate(validated_tables):
            df = getattr(table, attr)
            count = df.shape[1]
            column_names = list(df)
            renames: Dict[str, str] = {}

            for column_name in column_names:
                i = 1
                new_column_name = column_name
                while new_column_name in used_column_names:
                    new_column_name = '%s_%s' % (column_name, i)
                    i += 1
                if column_name != new_column_name:
                    renames[column_name] = new_column_name

            if renames:
                df = df.rename(columns=renames)

            used_column_names.update(list(df))
            tables.append(df)
            column_types.extend([column_type] * count)
            measurement_metadata.extend([index + 1] * count)

    merged = pandas.concat(tables, axis=1, join='inner')

    # create similar structure
    metadata = pandas.DataFrame(measurement_metadata).T
    metadata.columns = list(merged)
    metadata.index = ['Data Source']

    row_types = [
        TABLE_ROW_TYPES.INDEX,
        TABLE_ROW_TYPES.METADATA  # data source
    ] + ([TABLE_ROW_TYPES.DATA] * merged.shape[0])

    table = pandas.concat([metadata, merged])

    return table, column_types, row_types

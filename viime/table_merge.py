"""
This module contains methods related to mergind dataset
"""
from typing import Callable, Dict, List, Optional, Set

import pandas as pd

from .models import TABLE_COLUMN_TYPES, TABLE_ROW_TYPES, \
    ValidatedMetaboliteTable
from .opencpu import opencpu_request


def _merge_impl(validated_tables: List[ValidatedMetaboliteTable],
                transformer: Optional[Callable[[pd.DataFrame, int],
                                      pd.DataFrame]] = None):
    used_column_names: Set[str] = set()
    tables: List[pd.DataFrame] = []
    column_types: List[str] = [
        TABLE_COLUMN_TYPES.INDEX
    ]
    measurement_metadata: List[int] = []

    to_merge = [
        (TABLE_COLUMN_TYPES.GROUP, 'groups', False),
        (TABLE_COLUMN_TYPES.METADATA, 'sample_metadata', False),
        (TABLE_COLUMN_TYPES.DATA, 'measurements', True)
    ]
    for (column_type, attr, do_transform) in to_merge:
        for index, table in enumerate(validated_tables):
            df = getattr(table, attr)
            if do_transform and transformer:
                df = transformer(df, index)
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

    merged = pd.concat(tables, axis=1, join='inner')

    # create similar structure
    metadata = pd.DataFrame(measurement_metadata).T
    metadata.columns = list(merged)
    metadata.index = ['Data Source']

    row_types = [
        TABLE_ROW_TYPES.INDEX,
        TABLE_ROW_TYPES.METADATA  # data source
    ] + ([TABLE_ROW_TYPES.DATA] * merged.shape[0])

    table = pd.concat([metadata, merged])

    return table, column_types, row_types


def simple_merge(validated_tables: List[ValidatedMetaboliteTable]):
    """
    Generate a new validated csv file by concatonating a list of 2 or more
    validated tables.
    """

    return _merge_impl(validated_tables)


def _clean_pca_transformer(measurements: pd.DataFrame, index: int) -> pd.DataFrame:
    files = {
        'measurements': measurements.to_csv().encode()
    }
    params = {
        'prefix': 'DS%d' % (index + 1)
    }
    return opencpu_request('compute_clean_pca', files, params)


def clean_pca_merge(validated_tables: List[ValidatedMetaboliteTable]):
    return _merge_impl(validated_tables, _clean_pca_transformer)


merge_methods = dict(simple=simple_merge, clean=clean_pca_merge)

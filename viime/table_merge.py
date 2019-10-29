"""
This module contains methods related to mergind dataset
"""
from typing import Any, Callable, Dict, List, Optional, Set

import pandas as pd

from .models import TABLE_COLUMN_TYPES, TABLE_ROW_TYPES, \
    ValidatedMetaboliteTable
from .opencpu import opencpu_request


def _merge_impl(validated_tables: List[ValidatedMetaboliteTable],
                transformer: Optional[Callable[[pd.DataFrame, int],
                                      pd.DataFrame]] = None):
    used_column_names: Set[str] = set()
    tables: List[pd.DataFrame] = []
    column_types: List[Dict[str, Any]] = [
        dict(type=TABLE_COLUMN_TYPES.INDEX)
    ]
    measurement_metadata: List[int] = []

    def append_table(column_type: str, df: pd.DataFrame, index: int):
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
        column_types.extend([dict(type=column_type)] * count)
        measurement_metadata.extend([index + 1] * count)

    def append_tables(column_type: str, attr: str, do_transform=False):
        for index, table in enumerate(validated_tables):
            df = getattr(table, attr)
            if do_transform and transformer:
                df = transformer(df, index)
            append_table(column_type, df, index)

    append_tables(TABLE_COLUMN_TYPES.GROUP, 'groups', False)
    append_tables(TABLE_COLUMN_TYPES.METADATA, 'sample_metadata', False)
    append_tables(TABLE_COLUMN_TYPES.DATA, 'measurements', True)

    merged = pd.concat(tables, axis=1, join='inner')

    # create similar structure
    metadata = pd.DataFrame(measurement_metadata).T
    metadata.columns = list(merged)
    metadata.index = ['Data Source']

    levels = [dict(name=i + 1, label=t.name) for i, t in enumerate(validated_tables)]
    source_meta = dict(levels=levels)

    row_types = [
        dict(type=TABLE_ROW_TYPES.INDEX),
        dict(type=TABLE_ROW_TYPES.METADATA, subtype='categorical', meta=source_meta)  # data source
    ] + ([dict(type=TABLE_ROW_TYPES.DATA)] * merged.shape[0])

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


def _multi_block_transformer(measurements: pd.DataFrame, index: int) -> pd.DataFrame:
    files = {
        'measurements': measurements.to_csv().encode()
    }
    return opencpu_request('compute_multi_block', files)


def multi_block_merge(validated_tables: List[ValidatedMetaboliteTable]):
    return _merge_impl(validated_tables, _multi_block_transformer)


merge_methods = dict(simple=simple_merge, clean=clean_pca_merge,
                     multi_block=multi_block_merge)

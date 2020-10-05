from typing import Any, Dict, Optional

from marshmallow import ValidationError
import pandas as pd
from sklearn import preprocessing


NORMALIZATION_METHODS = {'minmax', 'sum', 'reference-sample', 'weight-volume'}


def validate_normalization_method(args: Dict[str, Any]):
    method = args.get('method', None)
    argument = args.get('argument', None)
    if method is not None and method not in NORMALIZATION_METHODS:
        raise ValidationError('Invalid normalization method', data=method)
    if method == 'reference-sample' and argument is None:
        raise ValidationError('Method requires argument', data=argument)


def normalize(method: str, table: pd.DataFrame, argument: Optional[Dict[str, Any]] = None,
              measurement_metadata: Optional[pd.DataFrame] = None,
              sample_metadata: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    if method is None:
        pass
    elif method == 'minmax':
        for column in table:
            column_data = table[[column]].values.astype(float)
            min_max_scalar = preprocessing.MinMaxScaler()
            table[[column]] = min_max_scalar.fit_transform(column_data)
    elif method == 'sum':
        table = sum(table)
    elif method == 'reference-sample':
        table = reference_sample(table, argument)
    elif method == 'weight-volume':
        table = weight_volume(table, argument, sample_metadata)
    else:
        raise Exception('Unknown normalization method')

    return table


def sum(table: pd.DataFrame) -> pd.DataFrame:
    return 1000 * table.div(table.sum(axis=1), axis=0)


def reference_sample(table: pd.DataFrame, argument) -> pd.DataFrame:
    return table.loc[argument].sum() * table.div(table.sum(axis=1), axis=0)


def weight_volume(table: pd.DataFrame, argument, sample_metadata: pd.DataFrame):
    if sample_metadata.dtypes[argument].name != 'float64':
        raise ValidationError('Column contains non-numeric data')
    return 100 * table.div(sample_metadata.loc[:, argument], axis=0)

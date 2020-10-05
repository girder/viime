from typing import Optional

import numpy as np
import pandas as pd

TRANSFORMATION_METHODS = {'log10', 'squareroot', 'cuberoot', 'log2'}


def transform(method: Optional[str], table: pd.DataFrame) -> pd.DataFrame:
    table = table.astype(np.float64)
    if method is None:
        table = table
    elif method == 'log10':
        table = log10(table)
    elif method == 'log2':
        table = log2(table)
    elif method == 'squareroot':
        table = squareroot(table)
    elif method == 'cuberoot':
        table = cuberoot(table)
    else:
        raise Exception('Unknown transform method')
    return table


def log10(table: pd.DataFrame, min=1e-8):
    return np.log10(table.clip(lower=min))


def log2(table: pd.DataFrame, min=1e-8):
    return np.log2(table.clip(lower=min))


def squareroot(table: pd.DataFrame):
    return np.sqrt(table.clip(lower=0))


def cuberoot(table: pd.DataFrame):
    return np.power(table.clip(lower=0), 1.0 / 3.0)

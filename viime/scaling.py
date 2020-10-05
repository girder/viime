from typing import Optional

import numpy as np
import pandas as pd

SCALING_METHODS = {'auto', 'range', 'pareto', 'vast', 'level'}


def scale(method: Optional[str], table: pd.DataFrame) -> pd.DataFrame:
    if method is None:
        pass
    elif method == 'auto':
        table = auto(table)
    elif method == 'range':
        table = range(table)
    elif method == 'pareto':
        table = pareto(table)
    elif method == 'vast':
        table = vast(table)
    elif method == 'level':
        table = level(table)
    else:
        raise Exception('Unknown scaling method')
    return table


def center(table: pd.DataFrame) -> pd.DataFrame:
    return table - table.mean()


def auto(table: pd.DataFrame) -> pd.DataFrame:
    return center(table) / table.std()


def range(table: pd.DataFrame) -> pd.DataFrame:
    return center(table) / (table.max() - table.min())


def pareto(table: pd.DataFrame) -> pd.DataFrame:
    return center(table) / np.sqrt(table.std())


def vast(table: pd.DataFrame) -> pd.DataFrame:
    mean = table.mean()
    sd = table.std()
    return (mean / sd) * (table - mean) / sd


def level(table: pd.DataFrame) -> pd.DataFrame:
    mean = table.mean()
    return (table - mean) / mean

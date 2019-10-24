from typing import Dict, List, Tuple, Union

import pandas as pd

from viime.cache import region
from viime.opencpu import opencpu_request

IMPUTE_MNAR_METHODS = ['zero', 'half-minimum']
IMPUTE_MCAR_METHODS = ['random-forest', 'knn', 'mean', 'median']


@region.cache_on_arguments()
def impute_missing(table: pd.DataFrame, groups: pd.DataFrame,
                   mnar='zero', mcar='random-forest', p_mnar=0.7, p_mcar=0.4,
                   add_info=False) -> Union[pd.DataFrame, Tuple[pd.DataFrame, List[str]]]:
    files = {
        'table': ('table.csv', table.to_csv().encode()),
        'groups': ('groups.csv', groups.to_csv().encode())
    }
    params = {
        'mnar': mnar,
        'mcar': mcar,
        'p_mnar': p_mnar,
        'p_mcar': p_mcar,
        'add_info': add_info
    }
    output: pd.DataFrame = opencpu_request('imputation', files=files, params=params)

    if add_info:
        columns: List[str] = list(output)
        renames = {c: c[2:] for c in columns}
        # A ... as is
        # C ... mcar
        # N ... mnar
        info: Dict[str, List[str]] = dict(mcar=[], mnar=[])
        for c in columns:
            if c[0] == 'C':
                info['mcar'].append(c[2:])
            elif c[0] == 'N':
                info['mnar'].append(c[2:])

        output = output.rename(columns=renames)
        return output, info

    return output

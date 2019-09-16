from itertools import combinations
from typing import Any, Dict, Optional

import pandas as pd
from scipy.stats import wilcoxon

from .opencpu import opencpu_request


def wilcoxon_test(measurements: pd.DataFrame, zero_method: Optional[str] = None,
                  alternative: Optional[str] = None) -> Dict[str, Any]:

    if zero_method is None:
        zero_method = 'wilcox'
    if alternative is None:
        alternative = 'two-sided'

    indices = list(measurements.index)
    data = []

    # test all possible combinations of rows
    for (x, y) in combinations(measurements.iterrows(), 2):
        x_index, x_data = x
        y_index, y_data = y
        (score, p) = wilcoxon(x_data, y_data, zero_method=zero_method, alternative=alternative)
        data.append(dict(x=x_index, y=y_index, score=score, p=p))

    return {
        'indices': indices,
        'data': data
    }


def anova_test(measurements: pd.DataFrame, groups: pd.Series) -> Dict[str, Any]:
    files = {
        'measurements': measurements.to_csv().encode(),
        'groups': groups.to_csv(header=True).encode()
    }

    data = opencpu_request('anova_turkey_adjustment', files, {})

    data = data.rename(columns={'(Intercept)': 'Intercept'})

    return {
        'groups': list(set(groups)),
        'pairs': list(data)[4:],
        'data': data.replace({pd.np.nan: None}).to_dict(orient='records')
    }

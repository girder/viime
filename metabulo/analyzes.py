from itertools import combinations
from typing import Dict, Any, Optional
import pandas as pd
from scipy.stats import wilcoxon


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

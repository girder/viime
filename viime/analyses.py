from itertools import combinations
from typing import Any, Dict, List, Optional

import pandas as pd

from .opencpu import opencpu_request


def wilcoxon_test(measurements: pd.DataFrame, groups: pd.Series) -> Dict[str, Any]:

    files = {
        'measurements': measurements.to_csv().encode(),
        'groups': groups.to_csv(header=True).encode()
    }

    data = opencpu_request('wilcoxon_test_z_scores', files, {})

    return {
        'groups': list(set(groups)),
        'pairs': list(data)[1:],
        'data': data.replace({pd.np.nan: None}).to_dict(orient='records')
    }


def anova_test(measurements: pd.DataFrame, groups: pd.Series) -> Dict[str, Any]:
    files = {
        'measurements': measurements.to_csv().encode(),
        'groups': groups.to_csv(header=True).encode()
    }

    data = opencpu_request('anova_tukey_adjustment', files, {})

    data = data.rename(columns={'(Intercept)': 'Intercept'})

    return {
        'groups': list(set(groups)),
        'pairs': list(data)[4:],
        'data': data.replace({pd.np.nan: None}).to_dict(orient='records')
    }


def pairwise_correlation(measurements: pd.DataFrame, min_correlation: float = 0,
                         method: Optional[str] = None) -> List[Dict]:

    corr = measurements.corr(method=method)

    r = []

    columns = list(corr)
    for (i, j) in combinations(range(0, len(corr)), 2):
        value = corr.iloc[i, j]
        if abs(value) > min_correlation:
            r.append(dict(x=columns[i], y=columns[j], value=value))

    return dict(columns=columns, correlations=r)

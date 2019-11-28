from io import StringIO
from itertools import combinations
from typing import Any, Dict, Optional

import pandas as pd

from .opencpu import opencpu_request


def clean(df: pd.DataFrame) -> pd.DataFrame:
    return df.replace([pd.np.nan, pd.np.Inf, -pd.np.Inf], None)


def wilcoxon_test(measurements: pd.DataFrame, groups: pd.Series) -> Dict[str, Any]:

    files = {
        'measurements': measurements.to_csv().encode(),
        'groups': groups.to_csv(header=True).encode()
    }

    data = opencpu_request('wilcoxon_test_z_scores', files, {
        'log_transformed': False  # TODO
    })

    return {
        'groups': list(set(groups)),
        'pairs': list(data)[1:],
        'data': clean(data).to_dict(orient='records')
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
        'data': clean(data).to_dict(orient='records')
    }


def hierarchical_clustering(measurements: pd.DataFrame) -> Dict[str, Any]:
    data = opencpu_request('clustered_heatmap', {
        'measurements': measurements.to_csv().encode()
    }, {}, return_type='json')

    values = pd.read_csv(StringIO('\n'.join(data['data'])), index_col=0).to_numpy()

    def create_node(n, all):
        if (not isinstance(n, list)):
            # -1 since R is 1 based
            return dict(name=all[n - 1], index=n - 1)
        return dict(children=[create_node(v, all) for v in n])

    return dict(values=values.tolist(),
                column=create_node(data['col'], list(measurements)),
                row=create_node(data['row'], list(measurements.index)))


def pairwise_correlation(measurements: pd.DataFrame, min_correlation: float = 0,
                         method: Optional[str] = None) -> Dict[str, Any]:

    corr = measurements.corr(method=method)

    r = []

    columns = list(corr)
    for (i, j) in combinations(range(0, len(corr)), 2):
        value = corr.iloc[i, j]
        if abs(value) > min_correlation:
            r.append(dict(x=columns[i], y=columns[j], value=value))

    return dict(columns=columns, correlations=r)

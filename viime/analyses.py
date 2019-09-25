from typing import Any, Dict

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage

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


def hierarchical_clustering(measurements: pd.DataFrame) -> Dict[str, Any]:
    r = linkage(measurements.to_numpy().T, optimal_ordering=True)
    df = pd.DataFrame(r.astype(np.int))
    df = df.rename(columns={
        0: 'a',
        1: 'b',
        2: 'distance',
        3: 'elements'
    })

    # number of metabolites
    columns = list(measurements)
    num_leaves = len(columns)
    tuples = list(df.itertuples())

    def create_node(index):
        print(index)
        if index < num_leaves:
            return dict(name=columns[index])
        # cluster
        entry = tuples[index - num_leaves]
        return dict(
            distance=entry.distance,
            value=entry.elements,
            children=[
                create_node(entry.a),
                create_node(entry.b)
            ]
        )

    return create_node(num_leaves + len(tuples) - 1)  # last is root

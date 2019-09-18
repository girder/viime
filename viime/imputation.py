from viime.cache import region
from viime.opencpu import opencpu_request

IMPUTE_MNAR_METHODS = ['zero', 'half-minimum']
IMPUTE_MCAR_METHODS = ['random-forest', 'knn', 'mean', 'median']


@region.cache_on_arguments()
def impute_missing(table, groups, mnar='zero', mcar='random-forest', p_mnar=0.7, p_mcar=0.4):
    files = {
        'table': ('table.csv', table.to_csv().encode()),
        'groups': ('groups.csv', groups.to_csv().encode())
    }
    params = {
        'mnar': mnar,
        'mcar': mcar,
        'p_mnar': p_mnar,
        'p_mcar': p_mcar
    }
    return opencpu_request('imputation', files=files, params=params)

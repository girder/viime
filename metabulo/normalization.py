from sklearn import preprocessing

from metabulo.cache import persistent_region

NORMALIZATION_METHODS = {'minmax', 'sum', 'reference-sample', 'weight-volume'}


@persistent_region.cache_on_arguments()
def normalize(method, table):
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
        table = reference_sample(table)
    elif method == 'weight-volume':
        table = weight_volume(table)
    else:
        raise Exception('Unknown normalization method')

    return table


def sum(table):
    return 1000 * table.div(table.sum(axis=1), axis=0)


def reference_sample(table):
    return table.iloc[0].sum() * table.div(table.sum(axis=1), axis=0)


def weight_volume(table):
    return 100 * table.div(table.iloc[:, 0], axis=0)

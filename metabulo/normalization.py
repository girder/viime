from sklearn import preprocessing

from metabulo.cache import region

NORMALIZATION_METHODS = {'minmax'}


@region.cache_on_arguments()
def normalize(method, table):
    if method is None:
        pass
    elif method == 'minmax':
        for column in table:
            column_data = table[[column]].values.astype(float)
            min_max_scalar = preprocessing.MinMaxScaler()
            table[[column]] = min_max_scalar.fit_transform(column_data)
    else:
        raise Exception('Unknown normalization method')

    return table

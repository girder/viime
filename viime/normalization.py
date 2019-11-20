from marshmallow import ValidationError
from sklearn import preprocessing

from viime.cache import persistent_region

NORMALIZATION_METHODS = {'minmax', 'sum', 'reference-sample', 'weight-volume'}


def validate_normalization_method(args):
    method = args.get('method', None)
    argument = args.get('argument', None)
    if method is not None and method not in NORMALIZATION_METHODS:
        raise ValidationError('Invalid normalization method', data=method)
    if method in ['reference-sample', 'weight-volume'] and argument is None:
        raise ValidationError('Method requires argument', data=argument)


@persistent_region.cache_on_arguments()
def normalize(method, table, argument=None, measurement_metadata=None, sample_metadata=None):
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
        table = reference_sample(table, argument)
    elif method == 'weight-volume':
        table = weight_volume(table, argument, sample_metadata)
    else:
        raise Exception('Unknown normalization method')

    return table


def sum(table):
    return 1000 * table.div(table.sum(axis=1), axis=0)


def reference_sample(table, argument):
    ref_sample = table.loc[argument]
    return ref_sample.sum() * table.div(table.sum(axis=1), axis=0)


def weight_volume(table, argument, sample_metadata):
    sample_weights = sample_metadata.loc[:, argument]
    return 100 * table.div(sample_weights, axis=0)

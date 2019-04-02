from functools import partial
from hashlib import sha256

from dogpile.cache import make_region
from dogpile.cache.util import kwarg_function_key_generator
from pandas.core.base import PandasObject
from pandas.util import hash_pandas_object


def hash_csv_file(csv_file):
    """Return a unique checksum for a csv_file model.

    This is designed to be as fast as possible, so it assumes the data
    contained in the csv is immutable.  The cache needs to be invalidated
    if the data can change.
    """
    # This will need to change if additional pipeline steps are added
    components = [csv_file.uri, csv_file.normalization or '']
    components += [r.row_type for r in csv_file.rows]
    components += [c.column_type for c in csv_file.columns]

    return sha256(''.join(components).encode()).hexdigest()


def hash_argument(arg):
    from metabulo.models import CSVFile  # circular import

    if isinstance(arg, PandasObject):
        r = hash_pandas_object(arg, index=True)
        return sha256(r.values.tostring()).hexdigest()
    elif isinstance(arg, CSVFile):
        return hash_csv_file(arg)

    return str(arg)


region = make_region(
    'metabulo.app',
    function_key_generator=partial(kwarg_function_key_generator, to_str=hash_argument)
).configure('dogpile.cache.null')

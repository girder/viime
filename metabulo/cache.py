from functools import partial
from hashlib import sha256

from dogpile.cache import make_region
from dogpile.cache.util import kwarg_function_key_generator
from pandas.core.base import PandasObject
from pandas.util import hash_pandas_object


def hash_argument(arg):
    if isinstance(arg, PandasObject):
        r = hash_pandas_object(arg, index=True)
        return sha256(r.values).hexdigest()
    return str(arg)


region = make_region(
    'metabulo.app',
    function_key_generator=partial(kwarg_function_key_generator, to_str=hash_argument)
).configure('dogpile.cache.null')

from functools import partial
from hashlib import sha256

from dogpile.cache import make_region
from dogpile.cache.backends.memory import MemoryBackend
from dogpile.cache.util import kwarg_function_key_generator
from flask import g
from pandas.core.base import PandasObject
from pandas.util import hash_pandas_object


def hash_argument(arg):
    from viime.models import CSVFile
    if isinstance(arg, PandasObject):
        r = hash_pandas_object(arg, index=True)
        return sha256(r.values.tostring()).hexdigest()
    elif isinstance(arg, CSVFile):
        return str(arg.id)

    return str(arg)


def mangle_key(key):
    return sha256(key.encode()).hexdigest()


def clear_cache(csv_file=None):
    g.cache = {}


class FlaskRequestLocalBackend(MemoryBackend):
    """This is a dogpile backend that is local to each request."""
    def __init__(self, arguments):
        pass

    @property
    def _cache(self):
        if 'cache' not in g:
            clear_cache()
        return g.cache


region = make_region(
    'viime.app.local',
    function_key_generator=partial(kwarg_function_key_generator, to_str=hash_argument)
)
region.configure('flask_request_local')

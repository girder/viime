from functools import partial
from hashlib import sha256

from dogpile.cache import make_region
from dogpile.cache.backends.memory import MemoryBackend
from dogpile.cache.util import kwarg_function_key_generator
from flask import g
from pandas.core.base import PandasObject
from pandas.util import hash_pandas_object

_cache_registry = []


def csv_file_cache(func):
    """Cache the results of a function acting on a csv file.

    The purpose of this decorator is to wrap the dogpile decorator, `cache_on_argument`.
    It keeps a registry of functions that have been decorated and adds the ability
    to purge the cache for all function calls on a specific model.

    ** This decorator only works with functions taking a single csv_file object as
    ** an argument.
    """
    func = persistent_region.cache_on_arguments()(func)
    _cache_registry.append(func)
    return func


def hash_argument(arg):
    from viime.models import CSVFile, TableColumn, TableRow
    if isinstance(arg, PandasObject):
        r = hash_pandas_object(arg, index=True)
        return sha256(r.values.tostring()).hexdigest()
    elif isinstance(arg, CSVFile):
        return str(arg.id)
    elif isinstance(arg, TableColumn):
        return str(arg.csv_file_id) + str(arg.column_index)
    elif isinstance(arg, TableRow):
        return str(arg.csv_file_id) + str(arg.row_index)

    return str(arg)


def mangle_key(key):
    return sha256(key.encode()).hexdigest()


def clear_cache(csv_file=None):
    g.cache = {}
    if csv_file:
        for func in _cache_registry:
            func.invalidate(csv_file)


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


persistent_region = make_region(
    'viime.app.persistent',
    function_key_generator=partial(kwarg_function_key_generator, to_str=hash_argument),
    key_mangler=mangle_key
)
persistent_region.configure('dogpile.cache.null')

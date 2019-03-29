from metabulo.cache import region
from metabulo.opencpu import opencpu_request


@region.cache_on_arguments()
def impute_missing(table, groups):
    files = {
        'table': ('table.csv', table.to_csv().encode()),
        'groups': ('groups.csv', groups.to_csv().encode())
    }
    return opencpu_request('imputation', files=files)

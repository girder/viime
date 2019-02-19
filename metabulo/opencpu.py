from io import BytesIO

import pandas
import requests


# TODO: accept extra params
def process_table(uri, table):
    files = {
        'table': ('table.csv', table.to_csv().encode())
    }
    req = requests.post(uri + '/csv?row.names=true', files=files)
    if not req.ok:
        print(req.content)
    assert req.ok
    return pandas.read_csv(BytesIO(req.content), index_col=0)


if __name__ == '__main__':
    import sys
    table = pandas.read_csv(sys.argv[2], index_col=0)
    print(process_table(sys.argv[1], table))

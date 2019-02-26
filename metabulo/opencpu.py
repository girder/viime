from io import BytesIO

from flask import current_app, Response
import pandas
import requests


# TODO: accept extra params
def process_table(uri, table):
    api_root = current_app.config['OPENCPU_API_ROOT']
    files = {
        'table': ('table.csv', table.to_csv().encode())
    }
    resp = requests.post(api_root + uri + '/csv?row.names=true', files=files)
    if not resp.ok:
        return Response(resp.content, status=resp.status_code, mimetype='text/plain')

    result = pandas.read_csv(BytesIO(resp.content), index_col=0)
    return Response(result.to_csv(), mimetype='text/csv')


def generate_image(uri, table, params=None):
    api_root = current_app.config['OPENCPU_API_ROOT']
    params = params or {}

    files = {
        'table': ('table.csv', table.to_csv().encode())
    }
    resp = requests.post(api_root + uri + '/png', files=files, params=params)
    if not resp.ok:
        return Response(resp.content, status=resp.status_code, mimetype='text/plain')
    return Response(resp.content, mimetype='image/png')


if __name__ == '__main__':
    import sys
    table = pandas.read_csv(sys.argv[2], index_col=0)
    print(process_table(sys.argv[1], table))

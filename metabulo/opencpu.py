from io import BytesIO

from flask import current_app, Response
import pandas
import requests


class OpenCPUException(Exception):
    def __init__(self, msg, method, response):
        super().__init__(self, msg)
        self.method = method
        self.response = response

    @property
    def error_response(self):
        return Response(self.response.content, status=self.response.status_code,
                        mimetype='text/plain')


def opencpu_request(method, files=None, params=None, return_type='csv'):
    files = files or {}
    params = params or {}
    url = current_app.config['OPENCPU_API_ROOT'] + '/metabulo/R/' + method
    if return_type == 'csv':
        url += '/csv?row.names=true'
    elif return_type == 'png':
        url += '/png'
    else:
        raise Exception('Unknown return type')

    try:
        resp = requests.post(url, files=files, data=params)
    except requests.exceptions.RequestException as e:
        raise OpenCPUException(f'Error connecting to OpenCPU server', method, e.response)

    if not resp.ok:
        raise OpenCPUException(f'OpenCPU error calling {method}', method, resp)

    result = resp.content
    if return_type == 'csv':
        result = pandas.read_csv(BytesIO(resp.content), index_col=0)
    return result


def process_table(method, table, params=None):
    files = {
        'table': ('table.csv', table.to_csv().encode())
    }
    result = opencpu_request(method, files=files, params=params)
    return Response(result.to_csv(), mimetype='text/csv')


def generate_image(method, table, params=None):
    files = {
        'table': ('table.csv', table.to_csv().encode())
    }
    return opencpu_request(method, files=files, params=params, return_type='png')


if __name__ == '__main__':
    import sys
    table = pandas.read_csv(sys.argv[2], index_col=0)
    print(process_table(sys.argv[1], table))

from io import BytesIO

from httmock import all_requests, HTTMock
import pandas
import pytest

from metabulo.opencpu import OpenCPUException, process_table

csv_data = """id,col1,col2
row1,0.5,2.0
row2,1.5,0.0
"""


@all_requests
def success(url, request):
    return {'status_code': 201, 'content': csv_data}


@all_requests
def failure(url, request):
    return {'status_code': 400, 'content': 'invalid request'}


def test_process_table_success(app):
    table = pandas.read_csv(BytesIO(csv_data.encode()))
    with app.app_context(), HTTMock(success):
        resp = process_table('/some/method', table)

    assert resp.status_code == 200
    assert resp.data.decode() == csv_data


def test_process_table_failure(app):
    table = pandas.read_csv(BytesIO(csv_data.encode()))
    with app.app_context(), HTTMock(failure), pytest.raises(OpenCPUException):
        process_table('/some/method', table)

from pathlib import Path

from flask import url_for

_test_file = Path(__file__).with_name('test.xlsx')


def test_upload_excel_file(client):
    data = {
        'file': (open(_test_file, 'rb'), 'test.xlsx',
                 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
        'meta': '{"foo": "bar"}'
    }
    resp = client.post(
        url_for('csv.upload_excel_file'), data=data, content_type='multipart/form-data')

    assert resp.status_code == 201
    res = resp.json
    assert type(res) == list
    assert len(res) == 2

    sheet1 = res[0]
    assert sheet1['name'] == 'test-A.csv'
    assert len(sheet1['columns']) == 3
    assert sheet1['meta'] == {'foo': 'bar'}

    sheet2 = res[1]
    assert sheet2['name'] == 'test-Sheet2.csv'
    assert len(sheet2['columns']) == 4
    assert sheet2['meta'] == {'foo': 'bar'}

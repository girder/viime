from io import StringIO

import pandas as pd
import pytest

from viime.models import _guess_table_structure, CSVFileSchema, db

csv_file_schema = CSVFileSchema()


def generate_csv_file(data):
    csv_file = csv_file_schema.load({
        'table': data,
        'name': 'test_csv_file.csv'
    })
    db.session.add(csv_file)
    db.session.commit()
    return csv_file


def test_no_header(app):
    with app.test_request_context():
        csv = generate_csv_file("""
a,1,2,3
b,4,5,6
c,7,8,9
""")
        db.session.commit()

        csv.header_row_index = None
        db.session.commit()

        assert csv.headers == ['col1', 'col2', 'col3', 'col4']
        assert list(csv.indexed_table.columns) == ['col2', 'col3', 'col4']


def test_no_primary_key(app):
    with app.test_request_context():
        csv = generate_csv_file("""
a,b,c
1,2,3
4,5,6
7,8,9
""")
        db.session.commit()

        csv.key_column_index = None
        db.session.commit()

        assert csv.keys == ['row1', 'row2', 'row3', 'row4']
        assert list(csv.indexed_table.index) == ['row2', 'row3', 'row4']


def test_no_header_or_primary_key(app):
    with app.test_request_context():
        csv = generate_csv_file("""
1,2,3
4,5,6
7,8,9
""")
        db.session.commit()

        csv.key_column_index = None
        csv.header_row_index = None
        db.session.commit()

        assert csv.headers == ['col1', 'col2', 'col3']
        assert list(csv.indexed_table.columns) == ['col1', 'col2', 'col3']

        assert csv.keys == ['row1', 'row2', 'row3']
        assert list(csv.indexed_table.index) == ['row1', 'row2', 'row3']


def test_set_primary_key(app):
    with app.test_request_context():
        csv = generate_csv_file("""
c1,g,--,c2,c3
10,a,r1,11,12
13,a,r2,14,15
16,b,r3,17,18
""")
        db.session.commit()

        csv.key_column_index = 2
        db.session.commit()

        assert csv.keys == ['--', 'r1', 'r2', 'r3']
        assert list(csv.measurement_table.index) == ['r1', 'r2', 'r3']


def test_set_header_row(app):
    with app.test_request_context():
        csv = generate_csv_file("""
r1,10,11,12
--,c1,c2,c3
r2,13,14,15
r3,16,17,18
""")
        db.session.commit()

        csv.header_row_index = 1
        db.session.commit()

        assert csv.headers == ['--', 'c1', 'c2', 'c3']
        assert list(csv.groups.columns) == ['c1']
        assert list(csv.measurement_table.columns) == ['c2', 'c3']


def test_set_primary_key_and_header_row(app):
    with app.test_request_context():
        csv = generate_csv_file("""
m1,a,m2,m3,m4
m5,g,--,c1,c2
m6,a,r1,14,15
m7,b,r2,17,18
""")
        db.session.commit()

        csv.header_row_index = 1
        csv.key_column_index = 2
        db.session.commit()

        assert csv.headers == ['m5', 'g', '--', 'c1', 'c2']
        assert list(csv.measurement_table.columns) == ['c1', 'c2']

        assert csv.keys == ['m2', '--', 'r1', 'r2']
        assert list(csv.measurement_table.index) == ['r1', 'r2']


def test_non_numeric_table(app):
    with app.test_request_context():
        csv = generate_csv_file("""
h1,h2,h3,h4
 a,g1, 2, 3
 b,g2, a, 6
 c,g3, 8, 9
""")
        db.session.commit()

        table = csv.measurement_table
        assert table.applymap(lambda s: isinstance(s, (float, int))).all().all()


GUESS_TABLE_DATA = [(
    """
h1,h2,h3,h4,h5
 a, g1, 2, 3, 4
 b, g2, a, 6, 1
 c, g3, 8, 9, 0
""",
    ['sample', 'sample', 'sample'],
    ['group', 'measurement', 'measurement', 'measurement'],
), (
    """
h1,h2,h3,h4
 a, 2, g1, 3
 b, 1, g2, 6
 c, 8, g3, 9
""",
    ['sample', 'sample', 'sample'],
    ['measurement', 'group', 'measurement'],
), (
    """
h1,h2,h3,h4,h5
 a, a, g1, 3, 1
 b, b, g2, 6, 4
 c, c, g3, 9, 5
""",
    ['sample', 'sample', 'sample'],
    ['group', 'masked', 'measurement', 'measurement'],
), (
    """
h1,h2,h3,h4
 1, 2, 3, 3
 0, 0, 1, 6
 5, 1, 0, 9
""",
    ['sample', 'sample', 'sample'],
    ['group', 'measurement', 'measurement'],
), (
    """
h1,h2,h3,h4
 1, 2, 3, 3
 a, b, c, d
 5, 1, 0, 9
""",
    ['sample', 'masked', 'sample'],
    ['group', 'measurement', 'measurement'],
), (
    """
h1,h2,h3,h4,h5
 a, g1, 1, 3, 3
 b, g2, 1, d, 9
 c, g3, 1, 9, 5
""",
    ['sample', 'sample', 'sample'],
    ['group', 'masked', 'measurement', 'measurement'],
)]


@pytest.mark.parametrize('table_data,rows,columns', GUESS_TABLE_DATA)
def test_guess_table_structure(table_data, rows, columns):
    table = pd.read_csv(StringIO(table_data), index_col=None, header=None)
    r, c = _guess_table_structure(table)
    assert rows == r[1:]
    assert columns == c[1:]

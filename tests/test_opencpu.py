import numpy as np
import pandas
from pandas.testing import assert_frame_equal

from viime.opencpu import opencpu_request


def test_echo(app):
    df = pandas.DataFrame(np.random.randint(0, 100, size=(10, 4)), columns=list('ABCD'))

    with app.app_context():
        out = opencpu_request('echo', {
            'table': df.to_csv().encode()
        })
        assert_frame_equal(df, out)

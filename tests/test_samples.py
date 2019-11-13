import json
from pathlib import Path

from pandas.testing import assert_frame_equal
import pytest

from viime import samples
from viime.models import CSVFile


samples_dir = Path(__file__).parent.parent / 'samples'


@pytest.mark.parametrize('fid', list(samples_dir.glob('*.json')))
def test_sample(app, fid):
    with open(fid, 'r') as f:
        data = json.load(f)

    with app.app_context():
        csv = samples.upload(data)
        assert samples.is_sample_file(csv)
        csv = samples.disable_sample(csv)
        assert not samples.is_sample_file(csv)
        csv = samples.enable_sample(csv, 'Test')
        assert samples.is_sample_file(csv)
        assert csv.sample_group == 'Test'

        info = samples.dump_info(csv)
        assert info.get('name') == csv.name
        assert info.get('id') == str(csv.id)

        groups = samples.list_samples()
        assert len(groups) == 1
        group0 = groups[0]
        assert group0.get('name') == 'Test'
        assert len(group0.get('files')) == 1
        assert group0['files'][0] == info

        dump = samples.dump(csv)
        assert dump['name'] == csv.name
        csv = samples.upload(dump)
        assert csv.name == dump['name']

        sample_id = csv.id
        icsv = samples.import_files([csv])
        assert len(icsv) == 1
        # since updated in place
        csv = CSVFile.query.get(sample_id)
        assert icsv[0].id != str(csv.id)
        assert_frame_equal(icsv[0].table, csv.table)

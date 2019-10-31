from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm.session import make_transient

from .models import CSVFile, db, ValidatedMetaboliteTable


def is_sample_file(csv: CSVFile) -> bool:
    return csv.sample_group is not None


def import_files(files: List[CSVFile]):
    # imported_ids = set(c.id for c in csv)
    # TODO extend with the merge sources

    for csv in files:
        new_id = uuid4()
        ori_id = csv.id
        table = csv.table

        # remove from session
        for sub in csv.columns + csv.rows + csv.group_levels:
            db.session.expunge(sub)
            make_transient(sub)
            sub.csv_file_id = new_id

        db.session.expunge(csv)
        make_transient(csv)

        # update releated things
        csv.id = new_id
        csv.created = datetime.utcnow()
        csv.meta = csv.meta.copy()
        csv.sample_group = None
        # extra option to mimic the _read_csv logic
        csv.save_table(table, index=False, header=False)

        db.session.add(csv)
        for sub in csv.columns + csv.rows + csv.group_levels:
            db.session.add(sub)

        v: ValidatedMetaboliteTable = ValidatedMetaboliteTable.query \
            .filter_by(csv_file_id=ori_id).first()
        if not v:
            continue

        db.session.expunge(v)
        make_transient(v)

        v.id = uuid4()
        v.csv_file_id = csv.id
        v.created = csv.created
        v.meta = csv.meta.copy()
        db.session.add(v)

    return files


def dump_info(csv: CSVFile):
    return dict(name=csv.name, description=csv.description, id=csv.id)


def list_samples():
    groups: Dict[str, List[CSVFile]] = {}
    for csv in CSVFile.query.filter(CSVFile.sample_group.isnot(None)).all():
        groups.setdefault(csv.sample_group, []).append(csv)
    return [dict(name=k, files=[dump_info(csv) for csv in v]) for k, v in groups.items()]


def dump(csv: CSVFile):
    # TODO reverse of upload
    return None


def upload(group: Optional[str]):
    # TODO reverse of dump
    return None

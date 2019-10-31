from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm.session import make_transient

from .models import CSVFile, db, ValidatedMetaboliteTable


def is_sample_file(csv: CSVFile) -> bool:
    return csv.sample_group is not None


def import_files(files: List[CSVFile]):
    new_ids = {str(c.id): uuid4() for c in files}

    todo = files.copy()

    while todo:
        csv = todo.pop(0)

        new_id = new_ids.get(str(csv.id))
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

        if 'merged' in csv.meta:
            # ensure we also merge the others
            merged_ids: List[str] = csv.meta['merged']
            new_merged_ids: List[str] = []
            for file_id in merged_ids:
                if file_id not in new_ids:
                    extra: CSVFile = CSVFile.query.get(file_id)
                    if extra:
                        extra_new_id = uuid4()
                        new_ids[extra.id] = extra_new_id
                        todo.append(extra)
                        new_merged_ids.append(str(extra_new_id))
                else:
                    new_merged_ids.append(str(new_ids[file_id]))
            csv.meta['merged'] = new_merged_ids

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

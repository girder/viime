from io import BytesIO

from flask import Blueprint, current_app, jsonify, request, send_file

from metabulo import opencpu
from metabulo.models import CSVFile, CSVFileSchema, db, \
    ModifyColumnSchema, ModifyRowSchema, \
    TABLE_COLUMN_TYPES, TABLE_ROW_TYPES, \
    TableColumn, TableColumnSchema, TableRow, \
    TableRowSchema, TableTransform, TableTransformSchema
from metabulo.plot import pca

csv_file_schema = CSVFileSchema()
modify_column_schema = ModifyColumnSchema()
modify_row_schema = ModifyRowSchema()
table_column_schema = TableColumnSchema(exclude=['csv_file'])
table_row_schema = TableRowSchema(exclude=['csv_file'])
table_transform_schema = TableTransformSchema()

csv_bp = Blueprint('csv', __name__)


@csv_bp.route('/csv/upload', methods=['POST'])
def upload_csv_file():
    if 'file' not in request.files:
        return jsonify('No file provided in request'), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify('No file selected'), 400

    csv_file = None
    try:
        csv_file = csv_file_schema.load({
            'name': file.filename,
            'table': file.read().decode()
        })

        db.session.add(csv_file)
        db.session.commit()

        return jsonify(csv_file_schema.dump(csv_file)), 201
    except Exception:
        if csv_file and csv_file.uri.is_file():
            csv_file.uri.unlink()
        db.session.rollback()
        raise


@csv_bp.route('/csv', methods=['POST'])
def create_csv_file():
    csv_file = None
    try:
        csv_file = csv_file_schema.load(request.json)
        db.session.add(csv_file)
        db.session.commit()

        return jsonify(csv_file_schema.dump(csv_file)), 201
    except Exception:
        if csv_file and csv_file.uri.is_file():
            csv_file.uri.unlink()
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>', methods=['GET'])
def get_csv_file(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    return jsonify(csv_file_schema.dump(csv_file))


@csv_bp.route('/csv/<uuid:csv_id>/download', methods=['GET'])
def download_csv_file(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    fp = BytesIO(csv_file.table.to_csv(header=False, index=False).encode())
    return send_file(fp, mimetype='text/csv', as_attachment=True, attachment_filename=csv_file.name)


@csv_bp.route('/csv/<uuid:csv_id>', methods=['DELETE'])
def delete_csv_file(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)

    try:
        TableRow.query.filter_by(csv_file_id=csv_id).delete()
        TableColumn.query.filter_by(csv_file_id=csv_id).delete()
        db.session.delete(csv_file)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    try:
        csv_file.uri.unlink()
    except Exception as e:
        current_app.logger.exception(e)

    return '', 204


# Row/Column API
@csv_bp.route('/csv/<uuid:csv_id>/column', methods=['GET'])
def list_columns(csv_id):
    CSVFile.query.get_or_404(csv_id)  # ensure the file exists
    return jsonify(table_column_schema.dump(
        TableColumn.query.filter_by(csv_file_id=csv_id),
        many=True
    ))


@csv_bp.route('/csv/<uuid:csv_id>/column/<int:column_index>', methods=['GET'])
def get_column(csv_id, column_index):
    return jsonify(table_column_schema.dump(
        TableColumn.query.get_or_404((csv_id, column_index))
    ))


@csv_bp.route('/csv/<uuid:csv_id>/column/<int:column_index>', methods=['PUT'])
def modify_column(csv_id, column_index):
    column = TableColumn.query.get_or_404((csv_id, column_index))
    csv_file = CSVFile.query.get_or_404(csv_id)
    args = modify_column_schema.load(request.json or {})
    for key, value in args.items():
        if key == 'column_type' and value == TABLE_COLUMN_TYPES.INDEX:
            csv_file.key_column_index = column_index
        else:
            setattr(column, key, value)
    db.session.add(column)
    db.session.add(csv_file)
    db.session.commit()
    return jsonify(table_column_schema.dump(column))


@csv_bp.route('/csv/<uuid:csv_id>/row', methods=['GET'])
def list_rows(csv_id):
    CSVFile.query.get_or_404(csv_id)  # ensure the file exists
    return jsonify(table_row_schema.dump(
        TableRow.query.filter_by(csv_file_id=csv_id),
        many=True
    ))


@csv_bp.route('/csv/<uuid:csv_id>/row/<int:row_index>', methods=['GET'])
def get_row(csv_id, row_index):
    return jsonify(table_row_schema.dump(
        TableRow.query.get_or_404((csv_id, row_index))
    ))


@csv_bp.route('/csv/<uuid:csv_id>/row/<int:row_index>', methods=['PUT'])
def modify_row(csv_id, row_index):
    row = TableRow.query.get_or_404((csv_id, row_index))
    csv_file = CSVFile.query.get_or_404(csv_id)
    args = modify_row_schema.load(request.json or {})
    for key, value in args.items():
        if key == 'row_type' and value == TABLE_ROW_TYPES.INDEX:
            csv_file.header_row_index = row_index
        else:
            setattr(row, key, value)
    db.session.add(row)
    db.session.add(csv_file)
    db.session.commit()
    return jsonify(table_row_schema.dump(row))


# Transform API
@csv_bp.route('/csv/<uuid:csv_id>/transform', methods=['POST'])
def create_transform(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    transform_ = csv_file.generate_transform(request.json or {})
    db.session.add(transform_)
    db.session.commit()
    return jsonify(table_transform_schema.dump(transform_)), 201


@csv_bp.route('/csv/<uuid:csv_id>/transform/<uuid:transform_id>', methods=['DELETE'])
def delete_transform(csv_id, transform_id):
    transform_ = TableTransform.query.get_or_404(transform_id)
    db.session.delete(transform_)
    db.session.commit()
    return '', 204


@csv_bp.route('/csv/<uuid:csv_id>/plot/pca', methods=['GET'])
def get_pca_plot(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    max_components = int(request.args.get('max_components', 5))
    data = pca(csv_file.measurement_table, max_components)

    labels = csv_file.sample_metadata.to_dict()

    def arraify(obj):
        return list(map(lambda i: obj['S{}'.format(i + 1)], range(len(obj.keys()))))

    data['labels'] = {k: arraify(v) for k, v in labels.items()}

    return jsonify(data), 200


@csv_bp.route('/csv/<uuid:csv_id>/pca-overview', methods=['GET'])
def get_pca_overview(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    return opencpu.generate_image('/metabulo/R/pca_overview_plot', csv_file.table)

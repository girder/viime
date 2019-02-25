from io import BytesIO

from flask import Blueprint, current_app, jsonify, request, send_file
from sklearn import preprocessing

from metabulo.models import CSVColumn, CSVFile, CSVFileSchema, db
from metabulo.opencpu import process_table


csv_file_schema = CSVFileSchema()

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
    fp = BytesIO(csv_file.table.to_csv().encode())
    return send_file(fp, mimetype='text/csv', as_attachment=True, attachment_filename=csv_file.name)


@csv_bp.route('/csv/<uuid:csv_id>', methods=['DELETE'])
def delete_csv_file(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    CSVColumn.query.filter_by(file_id=csv_id).delete()
    db.session.delete(csv_file)
    db.session.commit()

    try:
        csv_file.uri.unlink()
    except Exception as e:
        current_app.logger.exception(e)

    return '', 204


@csv_bp.route('/csv/<uuid:csv_id>/normalize/<column>', methods=['PUT'])
def normalize_row(csv_id, column):
    csv_file = CSVFile.query.get_or_404(csv_id)
    table = csv_file.table
    column_data = table[[column]].values.astype(float)
    min_max_scalar = preprocessing.MinMaxScaler()
    table[[column]] = min_max_scalar.fit_transform(column_data)

    return csv_file.save_table()

# @csv_bp.route('/csv/<uuid:csv_id>/normalize', methods=["PUT"])
# def normalize_rows(csv_id):
#     csv_file = CSVFile.query.get_or_404(csv_id)
#     table = csv_file.table


@csv_bp.route('/csv/<uuid:csv_id>/fill/<column>', methods=['PUT'])
def fill_missing_values(csv_id, column):
    value = request.json.get('value')
    csv_file = CSVFile.query.get_or_404(csv_id)
    table = csv_file.table
    if value is None:
        value = table[column].mean()
    table[column] = table[column].fillna(value)

    return csv_file.save_table()


@csv_bp.route('/csv/<uuid:csv_id>/echo', methods=['GET'])
def echo_csv_file(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    table = csv_file.table
    return process_table('/metabulo/R/echo', table)


@csv_bp.route('/csv/<uuid:csv_id>/demo', methods=['GET'])
def processing_demo(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    table = csv_file.table
    return process_table('/metabulo/R/demo', table)

from io import BytesIO

from flask import Blueprint, current_app, jsonify, request, send_file

from metabulo.models import CSVFile, CSVFileSchema, db, TableTransform, TableTransformSchema


csv_file_schema = CSVFileSchema()
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
    fp = BytesIO(csv_file.table.to_csv().encode())
    return send_file(fp, mimetype='text/csv', as_attachment=True, attachment_filename=csv_file.name)


@csv_bp.route('/csv/<uuid:csv_id>', methods=['DELETE'])
def delete_csv_file(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    db.session.delete(csv_file)
    db.session.commit()

    try:
        csv_file.uri.unlink()
    except Exception as e:
        current_app.logger.exception(e)

    return '', 204


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

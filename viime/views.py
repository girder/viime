from functools import wraps
from io import BytesIO
import json
import math
from pathlib import PurePath
from typing import Callable, cast, Dict, Optional
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request, Response, send_file
from marshmallow import fields, validate, ValidationError
import pandas
from webargs.flaskparser import use_kwargs
from werkzeug import FileStorage

from viime import opencpu
from viime.analyses import anova_test, pairwise_correlation, wilcoxon_test
from viime.cache import csv_file_cache
from viime.imputation import IMPUTE_MCAR_METHODS, IMPUTE_MNAR_METHODS
from viime.models import AXIS_NAME_TYPES, CSVFile, CSVFileSchema, db, \
    ModifyLabelListSchema, \
    TABLE_COLUMN_TYPES, TABLE_ROW_TYPES, \
    TableColumn, TableColumnSchema, TableRow, \
    TableRowSchema, ValidatedMetaboliteTable, ValidatedMetaboliteTableSchema
from viime.normalization import validate_normalization_method
from viime.plot import pca
from viime.scaling import SCALING_METHODS
from viime.table_validation import get_fatal_index_errors, ValidationSchema
from viime.transformation import TRANSFORMATION_METHODS

csv_file_schema = CSVFileSchema()
modify_label_list_schema = ModifyLabelListSchema()
table_column_schema = TableColumnSchema(exclude=['csv_file'])
table_row_schema = TableRowSchema(exclude=['csv_file'])
validation_schema = ValidationSchema()
validated_metabolite_table_schema = ValidatedMetaboliteTableSchema()

csv_bp = Blueprint('csv', __name__)


def load_validated_csv_file(func):

    @wraps(func)
    def wrapped(csv_id, *arg, **kwargs):
        csv_file = ValidatedMetaboliteTable.query \
            .filter_by(csv_file_id=csv_id) \
            .first_or_404()
        return func(csv_file, *arg, **kwargs)

    return wrapped


@csv_file_cache
def _serialize_csv_file(csv_file):
    csv_file_schema = CSVFileSchema()
    return csv_file_schema.dump(csv_file)


class JSONDictStr(fields.Dict):
    def _deserialize(self, value, *args, **kwargs):
        try:
            value = json.loads(value)
        except Exception:
            pass
        return super()._deserialize(value, *args, **kwargs)


@csv_bp.route('/csv/upload', methods=['POST'])
@use_kwargs({
    'file': fields.Field(location='files', validate=lambda f: f.content_type == 'text/csv'),
    'meta': JSONDictStr(missing=dict)
})
def upload_csv_file(file, meta):
    csv_file = None

    try:
        csv_file = csv_file_schema.load({
            'name': file.filename,
            'table': file.read().decode(errors='replace'),
            'meta': meta
        })

        db.session.add(csv_file)
        db.session.commit()

        return jsonify(_serialize_csv_file(csv_file)), 201
    except Exception:
        if csv_file and csv_file.uri.is_file():
            csv_file.uri.unlink()
        db.session.rollback()
        raise


_excel_mime_types = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
]


@csv_bp.route('/excel/upload', methods=['POST'])
@use_kwargs({
    'file': fields.Field(location='files', required=True,
                         validate=lambda f: f.content_type in _excel_mime_types),
    'meta': JSONDictStr(missing={})
})
def upload_excel_file(file: FileStorage, meta: Dict):
    excel_sheets = pandas.read_excel(file, sheet_name=None)  # type: Dict[str, pandas.DataFrame]
    excel_sheets = {sheet: data for (sheet, data) in excel_sheets.items() if not data.empty}

    basename = PurePath(cast(str, file.filename)).with_suffix('')

    try:
        db_files = []

        def push_file(name: PurePath, data: pandas.DataFrame):
            db_file = csv_file_schema.load({
                'name': name.with_suffix('.csv').name,
                'table': data.to_csv(index=False),
                'meta': meta
            })

            db_files.append(db_file)
            db.session.add(db_file)

        if len(excel_sheets) == 1:
            # single file case, simple name
            data = next(iter(excel_sheets.values()))
            push_file(basename, data)
        else:
            for sheet, data in excel_sheets.items():
                push_file(basename.with_name('%s-%s' % (basename.name, sheet)), data)

        db.session.flush()

        serialized = [_serialize_csv_file(f) for f in db_files]

        db.session.commit()

        return jsonify(serialized), 201
    except Exception:
        for f in db_files:
            if f.uri.is_file():
                f.uri.unlink()
        db.session.rollback()
        raise


@csv_bp.route('/csv/merge', methods=['POST'])
@use_kwargs({
    'csv_file_ids': fields.List(
        fields.UUID(), validate=validate.Length(min=2))
})
def merge_csv_files(csv_file_ids):
    """
    Generate a new validated csv file by concatonating a list of 2 or more
    validated tables.

    NOTE: This current uses the groups from the first table, removes
    all of the metadata, and does and "inner join" with the row indices"
    """
    tables = []
    for index, csv_file_id in enumerate(csv_file_ids):
        table = ValidatedMetaboliteTable.query.filter_by(
            csv_file_id=csv_file_id
        ).first()
        if index == 0:
            groups = table.groups

        if table is None:
            raise ValidationError(
                'One or more csv_files does not exist or is not validated')

        tables.append(table.measurements)

    merged = pandas.concat([groups] + tables, axis=1, join='inner')

    try:
        csv_file = csv_file_schema.load(dict(
            id=uuid4(),
            name='merged.csv',
            table=merged.to_csv(),
            meta={'merged': [str(id) for id in csv_file_ids]}
        ))
        db.session.add(csv_file)
        db.session.flush()

        validated_table = ValidatedMetaboliteTable.create_from_csv_file(csv_file)
        db.session.add(validated_table)

        response = _serialize_csv_file(csv_file)

        db.session.commit()
        return jsonify(response), 201
    except Exception:
        db.session.rollback()
        raise


@csv_bp.route('/csv', methods=['POST'])
def create_csv_file():
    csv_file = None
    try:
        csv_file = csv_file_schema.load(request.json)
        db.session.add(csv_file)
        db.session.commit()

        return jsonify(_serialize_csv_file(csv_file)), 201
    except Exception:
        if csv_file and csv_file.uri.is_file():
            csv_file.uri.unlink()
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>', methods=['GET'])
def get_csv_file(csv_id):
    csv_file = _serialize_csv_file(CSVFile.query.get_or_404(csv_id))

    # inject properties from the validated table model (normalization, transformation, etc.)
    validated_table = ValidatedMetaboliteTable.query.filter_by(csv_file_id=csv_id).first()
    if validated_table is not None:
        transformation_schema = ValidatedMetaboliteTableSchema(
            only=['normalization', 'normalization_argument', 'scaling',
                  'scaling', 'transformation']
        )
        transformation = transformation_schema.dump(validated_table)
        csv_file.update(transformation)

    return jsonify(csv_file)


@csv_bp.route('/csv/<uuid:csv_id>/validation', methods=['GET'])
def get_csv_file_validation(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    return jsonify(validation_schema.dump(csv_file.table_validation, many=True))


@csv_bp.route('/csv/<uuid:csv_id>/metadata', methods=['PUT'])
def set_csv_file_metadata(csv_id):
    try:
        csv_file = CSVFile.query.get_or_404(csv_id)
        csv_file.meta = request.json
        db.session.add(csv_file)
        db.session.commit()
        return jsonify(csv_file_schema.dump(csv_file))
    except Exception:
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>/name', methods=['PUT'])
@use_kwargs({
    'name': fields.Str(required=True)
})
def set_csv_file_name(csv_id, name):
    try:
        csv_file = CSVFile.query.get_or_404(csv_id)
        csv_file.name = name
        db.session.add(csv_file)
        db.session.commit()
        return jsonify(csv_file_schema.dump(csv_file))
    except Exception:
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>/description', methods=['PUT'])
@use_kwargs({
    'description': fields.Str(required=True)
})
def set_csv_file_description(csv_id, description):
    try:
        csv_file = CSVFile.query.get_or_404(csv_id)
        csv_file.description = description
        db.session.add(csv_file)
        db.session.commit()
        return jsonify(csv_file_schema.dump(csv_file))
    except Exception:
        db.session.rollback()
        raise


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

# Missing data imputation options
@csv_bp.route('/csv/<uuid:csv_id>/imputation', methods=['GET'])
def get_imputation_options(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    return jsonify({
        'imputation_mcar': csv_file.imputation_mcar,
        'imputation_mnar': csv_file.imputation_mnar
    })


@csv_bp.route('/csv/<uuid:csv_id>/imputation', methods=['PUT'])
@use_kwargs({
    'mcar': fields.Str(validate=validate.OneOf(IMPUTE_MCAR_METHODS)),
    'mnar': fields.Str(validate=validate.OneOf(IMPUTE_MNAR_METHODS))
})
def set_imputation_options(csv_id, **kwargs):
    csv_file = CSVFile.query.get_or_404(csv_id)

    try:
        if 'mcar' in kwargs:
            csv_file.imputation_mcar = kwargs['mcar']
        if 'mnar' in kwargs:
            csv_file.imputation_mnar = kwargs['mnar']
        db.session.add(csv_file)
        db.session.commit()
        return jsonify({
            'imputation_mcar': csv_file.imputation_mcar,
            'imputation_mnar': csv_file.imputation_mnar
        })
    except Exception:
        db.session.rollback()
        raise


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


@csv_bp.route('/csv/<uuid:csv_id>/batch/label', methods=['PUT'])
def batch_modify_label(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    args = modify_label_list_schema.load(request.json or {})
    row_column_dump_schema = CSVFileSchema(only=['rows', 'columns'])

    for change in args['changes']:
        index = change['index']
        label = change['label']
        context = change['context']

        if context == AXIS_NAME_TYPES.ROW:
            row = TableRow.query.get_or_404((csv_id, index))
            if label == TABLE_ROW_TYPES.INDEX:
                csv_file.header_row_index = index
            setattr(row, 'row_type', label)
            db.session.add(row)

        elif context == AXIS_NAME_TYPES.COLUMN:
            column = TableColumn.query.get_or_404((csv_id, index))
            if label == TABLE_COLUMN_TYPES.INDEX:
                csv_file.key_column_index = index
            elif label == TABLE_COLUMN_TYPES.GROUP:
                csv_file.group_column_index = index
            setattr(column, 'column_type', label)
            db.session.add(column)

    db.session.add(csv_file)

    try:
        db.session.commit()
        return jsonify(row_column_dump_schema.dump(csv_file))
    except Exception:
        db.session.rollback()
        raise


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


@csv_bp.route('/csv/<uuid:csv_id>/validate', methods=['POST'])
def save_validated_csv_file(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    fatal_errors = get_fatal_index_errors(csv_file)
    if fatal_errors:
        return jsonify(validation_schema.dump(fatal_errors, many=True)), 400

    old_table = ValidatedMetaboliteTable.query.filter_by(csv_file_id=csv_id)
    try:
        if old_table is not None:
            old_table.delete()
            db.session.commit()  # we actually want to persist to invalidate the old table

        validated_table = ValidatedMetaboliteTable.create_from_csv_file(csv_file)
        db.session.add(validated_table)
        db.session.commit()
        return jsonify(validated_metabolite_table_schema.dump(validated_table)), 201
    except Exception:
        db.session.rollback()
        raise


def serialize_validated_table(validated_table):
    try:
        return validated_metabolite_table_schema.dump(validated_table)
    except Exception as e:
        current_app.logger.exception(e)
        raise ValidationError('Error applying data transformation')


# Endpoints below here act on "ValidatedMetaboliteTable" rather "CSVFile"
@csv_bp.route('/csv/<uuid:csv_id>/normalization', methods=['PUT'])
@use_kwargs({
    'method': fields.Str(allow_none=True),
    'argument': fields.Str(allow_none=True)
}, validate=validate_normalization_method)
@load_validated_csv_file
def set_normalization_method(validated_table, **kwargs):
    method = kwargs['method']
    argument = kwargs.get('argument', None)

    try:
        validated_table.normalization = method
        validated_table.normalization_argument = argument
        serialized = serialize_validated_table(validated_table)
        db.session.add(validated_table)
        db.session.commit()
        return jsonify(serialized)
    except Exception:
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>/transformation', methods=['PUT'])
@load_validated_csv_file
def set_transformation_method(validated_table):
    args = request.json
    method = args['method']
    if method is not None and method not in TRANSFORMATION_METHODS:
        raise ValidationError('Invalid transformation method', data=method)
    try:
        validated_table.transformation = method
        serialized = serialize_validated_table(validated_table)
        db.session.add(validated_table)
        db.session.commit()
        return jsonify(serialized)
    except Exception:
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>/scaling', methods=['PUT'])
@load_validated_csv_file
def set_scaling_method(validated_table):
    args = request.json
    method = args['method']
    if method is not None and method not in SCALING_METHODS:
        raise ValidationError('Invalid scaling method', data=method)
    try:
        validated_table.scaling = method
        serialized = serialize_validated_table(validated_table)
        db.session.add(validated_table)
        db.session.commit()
        return jsonify(serialized)
    except Exception:
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>/validate/download', methods=['GET'])
@load_validated_csv_file
def download_validated_csv_file(validated_table):
    fp = BytesIO(validated_table.table.to_csv().encode())
    return send_file(fp, mimetype='text/csv', as_attachment=True,
                     attachment_filename=validated_table.name)


def _get_pca_data(validated_table):
    table = validated_table.measurements

    max_components = request.args.get('max_components')
    if max_components is None:
        rows, cols = table.shape[:2]
        max_components = min(rows, cols)
    else:
        max_components = int(max_components)

    data = pca(table, max_components)

    # insert per row label metadata information
    labels = validated_table.sample_metadata
    groups = validated_table.groups
    data['labels'] = pandas.concat([groups, labels], axis=1).to_dict('list')
    data['rows'] = table.index.tolist()

    return data


@csv_bp.route('/csv/<uuid:csv_id>/plot/pca', methods=['GET'])
@load_validated_csv_file
def get_pca_plot(validated_table):
    return jsonify(_get_pca_data(validated_table)), 200


def _get_loadings_data(validated_table):
    def mean(x):
        return sum(x) / len(x)

    def sq(x):
        return x * x

    def cor(xs, ys):
        if xs.equals(ys):
            return 1.0

        x_mean = mean(xs)
        y_mean = mean(ys)

        x_stddev = math.sqrt(sum(map(lambda x: sq(x - x_mean), xs)))
        y_stddev = math.sqrt(sum(map(lambda y: sq(y - y_mean), ys)))

        if x_stddev == 0 or y_stddev == 0:
            return 0.0

        prod_sum = sum(map(lambda x, y: (x - x_mean) * (y - y_mean), xs, ys))
        return prod_sum / (x_stddev * y_stddev)

    table = validated_table.measurements
    pca_data = _get_pca_data(validated_table)

    # Transpose the PCA values.
    pca_data = [list(x) for x in zip(*pca_data['x'])]

    # Compute correlations between each metabolite and both PC1 and PC2.
    return [{'col': k,
             'cor': [cor(v, pc) for pc in pca_data]}
            for (k, v) in table.items()]


@csv_bp.route('/csv/<uuid:csv_id>/plot/loadings', methods=['GET'])
@load_validated_csv_file
def get_loadings_plot(validated_table):
    return jsonify(_get_loadings_data(validated_table)), 200


@csv_bp.route('/csv/<uuid:csv_id>/pca-overview', methods=['GET'])
@load_validated_csv_file
def get_pca_overview(validated_table):
    png_content = opencpu.generate_image('/viime/R/pca_overview_plot',
                                         validated_table.measurements)
    return Response(png_content, mimetype='image/png')


def _group_test(method: Callable, validated_table: ValidatedMetaboliteTable,
                group_column: Optional[str] = None):
    measurements = validated_table.measurements
    groups = validated_table.groups

    group = groups.iloc[:, 0] if group_column is None else groups.loc[:, group_column]
    if group is None:
        raise ValidationError(
            'invalid group column', field_name='group_column', data=group_column)

    data = method(measurements, group)

    return jsonify(data), 200


@csv_bp.route('/csv/<uuid:csv_id>/analyses/wilcoxon', methods=['GET'])
@use_kwargs({
    'group_column': fields.Str(missing=None)
})
@load_validated_csv_file
def get_wilcoxon_test(validated_table: ValidatedMetaboliteTable,
                      group_column: Optional[str] = None):
    return _group_test(wilcoxon_test, validated_table, group_column)


@csv_bp.route('/csv/<uuid:csv_id>/analyses/anova', methods=['GET'])
@use_kwargs({
    'group_column': fields.Str()
})
@load_validated_csv_file
def get_anova_test(validated_table: ValidatedMetaboliteTable, group_column: Optional[str] = None):
    return _group_test(anova_test, validated_table, group_column)


@csv_bp.route('/csv/<uuid:csv_id>/analyses/correlation', methods=['GET'])
@use_kwargs({
    'min_correlation': fields.Float(missing=0.05, validate=validate.Range(0, 1)),
    'method': fields.Str(missing='pearson',
                         validate=validate.OneOf(['pearson', 'kendall', 'spearman']))
})
@load_validated_csv_file
def get_correlation(validated_table: ValidatedMetaboliteTable,
                    min_correlation: float, method: str):
    table = validated_table.measurements

    data = pairwise_correlation(table, min_correlation, method)

    return jsonify(data), 200

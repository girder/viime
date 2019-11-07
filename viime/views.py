from functools import wraps
from io import BytesIO
import json
from pathlib import PurePath
from typing import Callable, cast, Dict, List, Optional

from flask import Blueprint, current_app, jsonify, request, Response, send_file
from marshmallow import fields, validate, ValidationError
import pandas
from webargs.flaskparser import use_kwargs
from werkzeug import FileStorage

from viime import opencpu
from viime.analyses import anova_test, hierarchical_clustering, pairwise_correlation, wilcoxon_test
from viime.cache import csv_file_cache
from viime.imputation import IMPUTE_MCAR_METHODS, IMPUTE_MNAR_METHODS
from viime.models import AXIS_NAME_TYPES, CSVFile, CSVFileSchema, db, \
    GroupLevelSchema, ModifyLabelListSchema, \
    TABLE_COLUMN_TYPES, TABLE_ROW_TYPES, \
    TableColumn, TableColumnSchema, TableRow, \
    TableRowSchema, ValidatedMetaboliteTable, ValidatedMetaboliteTableSchema
from viime.normalization import validate_normalization_method
from viime.plot import pca
from viime.scaling import SCALING_METHODS
from viime.table_merge import merge_methods
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
    'file': fields.Field(location='files'),
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


@csv_bp.route('/excel/upload', methods=['POST'])
@use_kwargs({
    'file': fields.Field(location='files', required=True),
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


@csv_bp.route('/merge', methods=['POST'])
@use_kwargs({
    'name': fields.Str(required=True),
    'description': fields.Str(missing=None),
    'method': fields.Str(required=True, validate=validate.OneOf(merge_methods.keys())),
    'datasets': fields.List(
        fields.UUID(), validate=validate.Length(min=2))
})
def merge_csv_files(name: str, description: str, method: str, datasets: List[str]):
    tables = [ValidatedMetaboliteTable.query.filter_by(csv_file_id=id).first_or_404()
              for id in datasets]

    merged, column_types, row_types = merge_methods[method](tables)

    try:
        csv_file: CSVFile = csv_file_schema.load(dict(
            name=name,
            table=merged.to_csv(),
            meta={
                'merged': [str(id) for id in datasets],
                'merge_method': method
            }
        ))

        # update types afterwards since the default is auto generated

        if row_types:
            # update the row types
            for row, row_type in zip(csv_file.rows, row_types):
                row.row_type = row_type
                db.session.add(row)

        if column_types:
            # update the row types
            for column, column_type in zip(csv_file.columns, column_types):
                column.column_type = column_type
                db.session.add(column)

        # need to call it manually since we might have changed the column types
        csv_file.derive_group_levels(clear_caches=True)

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
                  'imputation_info',
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


@csv_bp.route('/csv/<uuid:csv_id>/group-levels', methods=['PUT'])
@use_kwargs({
    'group_levels': fields.List(fields.Nested(GroupLevelSchema(exclude=['csv_file_id'])),
                                required=True)
})
def set_csv_file_group_levels(csv_id, group_levels):
    try:
        csv_file = CSVFile.query.get_or_404(csv_id)
        csv_file.group_levels = group_levels
        db.session.add(csv_file)
        db.session.commit()
        return jsonify(csv_file_schema.dump(csv_file))
    except Exception:
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>/selected-columns', methods=['PUT'])
@use_kwargs({
    'columns': fields.List(fields.Str, required=True)
})
def set_csv_file_selected_columns(csv_id, columns):
    try:
        csv_file = CSVFile.query.get_or_404(csv_id)
        csv_file.selected_columns = columns
        db.session.add(csv_file)
        db.session.commit()

        return jsonify(csv_file_schema.dump(csv_file))
    except Exception:
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>/download', methods=['GET'])
def download_csv_file(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    name = PurePath(csv_file.name).with_suffix('.csv').name
    fp = BytesIO(csv_file.table.to_csv(header=False, index=False).encode())
    return send_file(fp, mimetype='text/csv', as_attachment=True, attachment_filename=name)


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
    row_column_dump_schema = CSVFileSchema(only=['rows', 'columns', 'group_levels'])

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


def _update_row_types(csv_file: CSVFile, row_types: Optional[str]):
    if row_types is None:
        return

    count_target = len(row_types)
    count_current = len(csv_file.rows)
    # update the row types
    for row, row_type in zip(csv_file.rows, row_types):
        row.row_type = row_type
        db.session.add(row)

    if count_target > count_current:
        # create missing
        for index, row_type in enumerate(row_types[count_current:]):
            row = table_row_schema.load({
                'csv_file_id': csv_file.id, 'row_index': index + count_current,
                'row_type': row_type
            })
            csv_file.rows.append(row)
            db.session.add(row)
    elif count_target < count_current:
        # delete extra
        for row in csv_file.rows[count_target:]:
            db.session.delete(row)


def _update_column_types(csv_file: CSVFile, column_types: Optional[str]):
    if column_types is None:
        return

    count_target = len(column_types)
    count_current = len(csv_file.columns)

    # update the column types

    for column, column_type in zip(csv_file.columns, column_types):
        column.column_type = column_type
        db.session.add(column)

    if count_target > count_current:
        # create missing
        for index, column_type in enumerate(column_types[count_current:]):
            column = table_column_schema.load({
                'csv_file_id': csv_file.id, 'column_index': index + count_current,
                'column_type': column_type
            })
            csv_file.columns.append(column)
            db.session.add(column)

    elif count_target < count_current:
        # delete extra
        for column in csv_file.column[count_target:]:
            db.session.delete(column)


@csv_bp.route('/csv/<uuid:csv_id>/remerge', methods=['POST'])
@use_kwargs({
    'method': fields.Str(missing=None, validate=validate.OneOf(merge_methods.keys())),
})
def remerge_csv_file(csv_id, method):
    try:
        csv_file: CSVFile = CSVFile.query.get_or_404(csv_id)
        if 'merged' not in csv_file.meta:
            raise ValidationError('given file is not a merged one')

        datasets = csv_file.meta['merged']
        if not method:
            method = csv_file.meta['merge_method']

        tables = [ValidatedMetaboliteTable.query.filter_by(csv_file_id=id).first_or_404()
                  for id in datasets]

        merged, column_types, row_types = merge_methods[method](tables)

        csv_file.save_table(merged)

        _update_column_types(csv_file, column_types)
        _update_row_types(csv_file, row_types)

        # need to call it manually since we might have changed the column types
        csv_file.derive_group_levels(clear_caches=True)

        meta = csv_file.meta.copy()
        meta.update({
            'merged': [str(id) for id in datasets],
            'merge_method': method
        })
        csv_file.meta = meta

        db.session.add(csv_file)
        db.session.commit()
        return jsonify(csv_file_schema.dump(csv_file))
    except Exception:
        db.session.rollback()
        raise


@csv_bp.route('/csv/<uuid:csv_id>/validate', methods=['POST'])
def save_validated_csv_file(csv_id):
    csv_file = CSVFile.query.get_or_404(csv_id)
    fatal_errors = get_fatal_index_errors(csv_file)
    if fatal_errors:
        return jsonify(validation_schema.dump(fatal_errors, many=True)), 400

    old_table = ValidatedMetaboliteTable.query.filter_by(csv_file_id=csv_id).first()
    try:
        old = {}
        if old_table is not None:
            transformation_schema = ValidatedMetaboliteTableSchema(
                only=['normalization', 'normalization_argument',
                      'scaling', 'transformation']
            )
            # copy some values
            old = transformation_schema.dump(old_table)

            db.session.delete(old_table)
            db.session.commit()  # we actually want to persist to invalidate the old table

        validated_table = ValidatedMetaboliteTable.create_from_csv_file(csv_file, **old)
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
@use_kwargs({
    'transpose': fields.Boolean(missing=False),
    'columns': fields.Str(missing='all', validate=validate.OneOf(['all', 'not-selected',
                                                                  'selected', 'none'])),
    'rows': fields.Str(missing=None)
})
@load_validated_csv_file
def download_validated_csv_file(validated_table: ValidatedMetaboliteTable,
                                transpose: bool,
                                columns: str, rows: Optional[str]):
    table: pandas.DataFrame = validated_table.table
    csv_file: CSVFile = CSVFile.query.get_or_404(validated_table.csv_file_id)

    nr_col_meta = validated_table.groups.shape[1] + validated_table.sample_metadata.shape[1]
    nr_row_meta = validated_table.measurement_metadata.shape[0]

    if columns == 'none':
        table = table.iloc[:, []]
    elif columns == 'selected':
        selected = list(table)[:nr_col_meta] + (csv_file.selected_columns or [])
        table = table.loc[:, selected]
    elif columns == 'not-selected':
        meta = list(table)[:nr_col_meta]
        not_selected = [c for c in table if c in meta or str(c) not in csv_file.selected_columns]
        table = table.loc[:, not_selected]

    if rows is not None:
        groups = table.iloc[:, 0]  # first column is group
        valid = list(groups[:nr_row_meta]) + rows.split(',')
        mask = [r in valid for r in groups]
        table = table.loc[mask, :]

    if transpose:
        table = table.T

    fp = BytesIO(table.to_csv().encode())
    name = PurePath(csv_file.name).with_suffix('.csv').name
    return send_file(fp, mimetype='text/csv', as_attachment=True,
                     attachment_filename=name)


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
    table = validated_table.measurements
    pca_data = _get_pca_data(validated_table)
    loadings = pca_data['rotation']

    # Extract the correlations between each metabolite and all PCs.
    return [{'col': k,
             'loadings': loadings[i]}
            for i, k in enumerate(table)]


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


@csv_bp.route('/csv/<uuid:csv_id>/analyses/heatmap', methods=['GET'])
@use_kwargs({
    'columns': fields.Str(required=False, missing=None,
                          validate=validate.OneOf(['selected', 'not-selected']))
})
@load_validated_csv_file
def get_hierarchical_clustering_heatmap(validated_table: ValidatedMetaboliteTable,
                                        columns: Optional[str]):
    table = validated_table.measurements

    if columns:
        csv_file: CSVFile = CSVFile.query.get_or_404(validated_table.csv_file_id)
        if columns == 'selected':
            table = table.loc[:, csv_file.selected_columns or []]
        elif columns == 'not-selected' and csv_file.selected_columns:
            non_selected = [c for c in table if str(c) not in csv_file.selected_columns]
            table = table.loc[:, non_selected]

    return hierarchical_clustering(table)


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

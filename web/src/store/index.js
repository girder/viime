import { cloneDeep } from 'lodash';
import Vue from 'vue';
import Vuex from 'vuex';

import {
  convertCsvToRows, RangeList, mapValidationErrors, parsePandasDataFrame,
} from '../utils';
import analyses from '../components/vis/analyses';
import { plot_types } from '../utils/constants';
import { CSVService, ExcelService } from '../common/api.service';

import {
  CHANGE_AXIS_LABEL,
  MUTEX_TRANSFORM_TABLE,
  LOAD_DATASET,
  LOAD_PLOT,
  LOAD_SESSION,
  UPLOAD_CSV,
  UPLOAD_EXCEL,
  CHANGE_IMPUTATION_OPTIONS,
} from './actions.type';

import {
  REMOVE_DATASET,
  SET_PLOT,
  SET_SELECTION,
  SET_DATASET_DESCRIPTION,
  SET_DATASET_NAME,
} from './mutations.type';

// private mutations
const INITIALIZE_DATASET = 'initialize_dataset';
const INVALIDATE_PLOTS = 'invalidate_plots';
const SET_DATASET_DATA = 'set_dataset_data';
const SET_VALIDATED_DATASET_DATA = 'set_validated_dataset_data';
const MERGE_INTO_DATASET = 'merge_into_dataset';
const SET_LABELS = 'set_labels';
const SET_LAST_ERROR = 'set_last_error';
const SET_LOADING = 'set_loading';
const SET_SESSION_STORE = 'set_session_store';
const SET_TRANSFORMATION = 'set_transformation';

Vue.use(Vuex);

const datasetDefaults = {
  description: '',
  created: new Date(),
  ready: false,
  validation: [],
  sourcerows: [],
  width: 0,
  height: 0,
  imputationMCAR: null,
  imputationMNAR: null,
  normalization: null,
  normalization_argument: null,
  transformation: null,
  transformation_argument: null,
  scaling: null,
  scaling_argument: null,

  measurement_table: null,

  validatedMeasurements: null,
  validatedGroups: null,
  validatedMeasurementsMetaData: null,
  validatedSampleMetaData: null,
};

const plotDefaults = {
  pca: {
    data: null,
    valid: false,
    loading: false,
    args: {},
    type: plot_types.TRANSFORM,
  },
  loadings: {
    data: null,
    valid: false,
    loading: false,
    args: {},
    type: plot_types.TRANSFORM,
  },
};

analyses.forEach(({
  args,
  path,
  type,
}) => {
  plotDefaults[path] = {
    data: null,
    valid: false,
    loading: false,
    args,
    type,
  };
});

const appstate = {
  datasets: {},
  plots: {},
  analyses: {},
  lasterror: null,
  loading: false,
  store: null, /** @type {WindowLocalStorage} */
  session_id: 'default',
};

const getters = {
  dataset: state => id => state.datasets[id],
  ready: state => id => state.datasets[id] && state.datasets[id].ready,
  // valid indicates fatal errors, and will be true even if there are warnings
  valid: state => id => getters.ready(state)(id)
    && state.datasets[id].validation.filter(v => v.severity === 'error').length === 0,
  txType: state => (id, category) => getters.ready(state)(id)
    && state.datasets[id][category],
  plot: state => (id, name) => getters.ready(state)(id) && state.plots[id][name],
};


const mutations = {
  /**
   * @private
   */
  [INVALIDATE_PLOTS](state, { dataset_id }) {
    const plots = Object.keys(plotDefaults);
    plots.forEach(name => Vue.set(state.plots[dataset_id][name], 'valid', false));
  },

  /**
   * @private
   */
  [INITIALIZE_DATASET](state, { dataset_id, name }) {
    Vue.set(state.plots, dataset_id, cloneDeep(plotDefaults));
    Vue.set(state.datasets, dataset_id, {
      ...datasetDefaults,
      id: dataset_id,
      name,
      selected: {
        type: 'column',
        last: 1,
        ranges: new RangeList([1]),
      },
    });
  },

  /**
   * @private
   */
  [SET_DATASET_DATA](state, { data }) {
    const {
      id, name, size, created, description,
    } = data;
    const { data: sourcerows } = convertCsvToRows(data.table);
    const measurement_table = parsePandasDataFrame(data.measurement_table);
    const oldData = state.datasets[id];
    Vue.set(state.datasets, id, {
      ...oldData,
      ...{
        name,
        description,
        created: new Date(created),
        size,
        ready: true,
        width: sourcerows[0].length,
        height: sourcerows.length,
        validation: mapValidationErrors(data.table_validation, data.columns),
        sourcerows,
        imputationMCAR: data.imputation_mcar,
        imputationMNAR: data.imputation_mnar,
        normalization: data.normalization,
        normalization_argument: data.normalization_argument,
        transformation: data.transformation,
        scaling: data.scaling,

        // imputed measurements
        measurement_table,

        // reset
        validatedMeasurements: null,
        validatedGroups: null,
        validatedMeasurementsMetaData: null,
        validatedSampleMetaData: null,
      },
    });
  },
  /**
   * @private
   */
  [SET_VALIDATED_DATASET_DATA](state, { data }) {
    const ds = state.datasets[data.csv_file_id];
    // the imputed table index are column can be used for all the other ones
    const base = ds.measurement_table;
    const validatedMeasurements = parsePandasDataFrame(data.measurements, base);
    const validatedGroups = parsePandasDataFrame(data.groups, base);
    const validatedMeasurementsMetaData = parsePandasDataFrame(data.measurement_metadata, base);
    const validatedSampleMetaData = parsePandasDataFrame(data.sample_metadata, base);

    const delta = {
      validatedMeasurements,
      validatedGroups,
      validatedMeasurementsMetaData,
      validatedSampleMetaData,
    };

    Object.entries(delta).forEach(([k, v]) => {
      Vue.set(ds, k, v);
    });
  },
  /**
   * @private
   */
  [MERGE_INTO_DATASET](state, { dataset_id, data }) {
    const ds = state.datasets[dataset_id];
    Object.entries(data).forEach(([k, v]) => {
      Vue.set(ds, k, v);
    });
  },

  /**
   * Set labels from server
   * @private
   */
  [SET_LABELS](state, { dataset_id, rows, columns }) {
    const rowsSorted = rows.sort((a, b) => a.row_index - b.row_index);
    const colsSorted = columns.sort((a, b) => a.column_index - b.column_index);
    Vue.set(state.datasets[dataset_id], 'row', {
      labels: rowsSorted.map(r => r.row_type),
      data: rowsSorted,
    });
    Vue.set(state.datasets[dataset_id], 'column', {
      labels: colsSorted.map(c => c.column_type),
      data: colsSorted,
    });
  },

  [REMOVE_DATASET](state, { dataset_id }) {
    Vue.delete(state.datasets, dataset_id);
    state.store.save(state, state.session_id);
  },

  /**
   * @private
   */
  [SET_LAST_ERROR](state, { err }) {
    Vue.set(state, 'lasterror', err);
  },

  /**
   * @private
   */
  [SET_LOADING](state, loading) {
    Vue.set(state, 'loading', loading);
  },

  [SET_PLOT](state, { dataset_id, name, obj }) {
    const plot = state.plots[dataset_id][name];
    Vue.set(state.plots[dataset_id], name, { ...plot, ...obj });
  },

  [SET_SELECTION](state, {
    key, event, axis, idx,
  }) {
    const { last, ranges, type } = state.datasets[key].selected;
    state.datasets[key].selected.last = idx;
    if (event.shiftKey && axis === type) {
      ranges.add(last, idx);
    } else if (event.ctrlKey && axis === type) {
      ranges.add(idx);
    } else if (!event.ctrlKey && !event.shiftKey) {
      state.datasets[key].selected.ranges = new RangeList([idx]);
      state.datasets[key].selected.type = axis;
    }
  },

  /**
   * @private
   */
  [SET_SESSION_STORE](state, { store, session_id }) {
    Vue.set(state, 'store', store);
    Vue.set(state, 'session_id', session_id);
  },

  /**
   * @private
   */
  [SET_TRANSFORMATION](state, {
    dataset_id, transform_type, category, argument,
  }) {
    Vue.set(state.datasets[dataset_id], category, transform_type);
    Vue.set(state.datasets[dataset_id], `${category}_argument`, argument);
  },
};

const actions = {

  async [UPLOAD_CSV]({ state, commit }, { file }) {
    commit(SET_LOADING, true);
    try {
      const { data } = await CSVService.upload(file);
      commit(INITIALIZE_DATASET, { dataset_id: data.id, name: data.name });
      commit(SET_LABELS, { dataset_id: data.id, rows: data.rows, columns: data.columns });
      commit(SET_DATASET_DATA, { data });
      state.store.save(state, state.session_id);
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [UPLOAD_EXCEL]({ state, commit }, { file }) {
    commit(SET_LOADING, true);
    try {
      const { data } = await ExcelService.upload(file);
      data.forEach((dataFile) => {
        commit(INITIALIZE_DATASET, { dataset_id: dataFile.id, name: data.name });
        commit(SET_LABELS, {
          dataset_id: dataFile.id,
          rows: dataFile.rows,
          columns: dataFile.columns,
        });
        commit(SET_DATASET_DATA, { data: dataFile });
      });
      state.store.save(state, state.session_id);
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  /**
   * reload dataset from server and checkpoint if the dataset is valid
   * @private
   */
  async [LOAD_DATASET]({ getters: _getters, commit }, { dataset_id }) {
    try {
      const dataset = _getters.dataset(dataset_id);
      if (!dataset) {
        commit(INITIALIZE_DATASET, { dataset_id });
      }
      const { data } = await CSVService.get(dataset_id);
      commit(SET_LABELS, { dataset_id, rows: data.rows, columns: data.columns });
      commit(SET_DATASET_DATA, { data });
      const valid = _getters.valid(dataset_id);
      if (valid) {
        const { data: validatedData } = await CSVService.validateTable(dataset_id);
        commit(SET_VALIDATED_DATASET_DATA, { data: validatedData });
      }
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      throw err;
    }
  },

  /**
   * if the plot is out of date and another request is not outstanding,
   * load the requested plot data from server.
   */
  async [LOAD_PLOT]({ getters: _getters, commit }, { dataset_id, name }) {
    const plot = _getters.plot(dataset_id, name);
    if (plot) {
      const {
        loading, valid, args, type: plotType,
      } = plot;
      if (!valid && !loading) {
        try {
          commit(SET_PLOT, { dataset_id, name, obj: { loading: true } });
          let d;
          switch (plotType) {
            case plot_types.TRANSFORM:
              ({ data: d } = await CSVService.getPlot(dataset_id, name, args));
              break;
            case plot_types.ANALYSIS:
              ({ data: d } = await CSVService.getAnalysis(dataset_id, name, args));
              break;
            default:
              throw new Error('Plot type unknown:', plotType);
          }
          commit(SET_PLOT, { dataset_id, name, obj: { loading: false, data: d, valid: true } });
        } catch (err) {
          commit(SET_PLOT, { dataset_id, name, obj: { loading: false, valid: false } });
          commit(SET_LAST_ERROR, err);
          throw err;
        }
      }
    }
  },

  /**
   * @param {Object} vuex
   * @param {import('../utils').SessionStore} sessionStore Store
   */
  async [LOAD_SESSION]({ commit, dispatch }, store, session_id = 'default') {
    commit(SET_LOADING, true);
    commit(SET_SESSION_STORE, { store, session_id });
    try {
      const { datasets } = store.load(session_id);
      await Promise.all(Object.keys(datasets).map(async (dataset_id) => {
        const data = datasets[dataset_id];
        commit(INITIALIZE_DATASET, { dataset_id: data.id, name: data.name });
        try {
          await dispatch(LOAD_DATASET, { dataset_id: data.id });
        } catch (err) {
          commit(REMOVE_DATASET, { dataset_id: data.id });
          throw err;
        }
      }));
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [MUTEX_TRANSFORM_TABLE]({ commit }, {
    category, dataset_id, transform_type, argument,
  }) {
    const key = dataset_id;
    commit(SET_LOADING, true);
    try {
      const { data } = await CSVService.setTransform(key, category, transform_type, argument);
      commit(SET_VALIDATED_DATASET_DATA, { data });
      commit(SET_TRANSFORMATION, {
        dataset_id, transform_type, category, argument,
      });
      commit(INVALIDATE_PLOTS, { dataset_id });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [CHANGE_AXIS_LABEL]({ dispatch, commit }, { dataset_id, changes }) {
    commit(SET_LOADING, true);
    try {
      const { data } = await CSVService.updateLabel(dataset_id, changes);
      const { rows, columns } = data;
      commit(SET_LABELS, { dataset_id, rows, columns });
      await dispatch(LOAD_DATASET, { dataset_id });
      // must await before plot invalidation because a new checkpoint
      // needs to be created before plots can be refreshed
      commit(INVALIDATE_PLOTS, { dataset_id });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [CHANGE_IMPUTATION_OPTIONS]({ dispatch, commit }, { dataset_id, options }) {
    commit(SET_LOADING, true);
    await CSVService.setImputation(dataset_id, options);
    await dispatch(LOAD_DATASET, { dataset_id });
    commit(INVALIDATE_PLOTS, { dataset_id });
    commit(SET_LOADING, false);
  },

  async [SET_DATASET_NAME]({ commit }, { dataset_id, name }) {
    commit(SET_LOADING, true);
    try {
      await CSVService.setName(dataset_id, name);
      commit(MERGE_INTO_DATASET, { dataset_id, data: { name } });
      commit(SET_LOADING, false);
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
  },

  async [SET_DATASET_DESCRIPTION]({ commit }, { dataset_id, description }) {
    commit(SET_LOADING, true);
    try {
      await CSVService.setDescription(dataset_id, description);
      commit(MERGE_INTO_DATASET, { dataset_id, data: { description } });
      commit(SET_LOADING, false);
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
  },

};

export default new Vuex.Store({
  state: appstate,
  getters,
  mutations,
  actions,
});

import { cloneDeep } from 'lodash';
import Vue from 'vue';
import Vuex from 'vuex';

import {
  convertCsvToRows, RangeList, mapValidationErrors,
} from '../utils';
import { CSVService } from '../common/api.service';
import analyses from '../components/analyze';

import {
  CHANGE_AXIS_LABEL,
  MUTEX_TRANSFORM_TABLE,
  LOAD_PLOT,
  LOAD_SESSION,
  UPLOAD_CSV,
  CHANGE_IMPUTATION_OPTIONS,
  CHANGE_ANALYSIS_OPTIONS,
} from './actions.type';

import {
  REFRESH_PLOT,
  REMOVE_DATASET,
  SET_DATASET,
  SET_LAST_ERROR,
  SET_LOADING,
  SET_LABELS,
  SET_SELECTION,
  SET_SESSION_STORE,
  SET_SOURCE_DATA,
  SET_TRANSFORMATION,
  SET_ANALYSIS_OPTIONS,
  SET_ANALYSIS_DATA,
  SET_ANALYSIS_STATE,
} from './mutations.type';

Vue.use(Vuex);

const plotDefaults = {
  // logic for which mutations invalidate plot data cache is internal to vuex state
  // this could be more granular.  for now, mutations invalidate all plots.
  // enumerate plot types
  pca: {
    data: null,
    valid: false,
  },
  loadings: {
    data: null,
    valid: false,
  },
};

const analysisDefaults = {};
analyses.forEach(({ options, path, key }) => {
  analysisDefaults[key || path] = {
    options,
    data: null,
    state: 'initial', // initial,computing,error,ready
  };
});

const appstate = {
  // map of all datasets in the session by csv UUID
  datasets: {},
  plots: {},
  analyses: {},
  lasterror: null,
  loading: false,
  /** @type {WindowLocalStorage} */
  store: null,
  session_id: 'default',
};

const getters = {
  dataset: state => id => state.datasets[id],
  ready: state => id => state.datasets[id] && state.datasets[id].ready,
  valid: state => id => getters.ready(state)(id)
    && state.datasets[id].validation.filter(v => v.severity === 'error').length === 0,
  txType: state => (id, category) => getters.ready(state)(id)
    && state.datasets[id][category],
  plotData: state => (id, name) => getters.ready(state)(id) && state.plots[id][name].data,
  plotValid: state => (id, name) => getters.ready(state)(id) && state.plots[id][name].valid,
  analysisOptions: state => (id, name) => getters.ready(state)(id)
    && state.analyses[id][name].options,
  analysisData: state => (id, name) => getters.ready(state)(id) && state.analyses[id][name].data,
  analysisState: state => (id, name) => getters.ready(state)(id) && state.analyses[id][name].state,
};

/*
 * Private mutation helpers
 */
function _invalidatePlots(state, { key, plotList }) {
  plotList.forEach((name) => {
    Vue.set(state.plots[key][name], 'valid', false);
  });
}
function _setLables(state, { key, rows, columns }) {
  _invalidatePlots(state, { key, plotList: ['pca', 'loadings'] });
  const rowsSorted = rows.sort((a, b) => a.row_index - b.row_index);
  const colsSorted = columns.sort((a, b) => a.column_index - b.column_index);
  Vue.set(state.datasets[key], 'row', {
    labels: rowsSorted.map(r => r.row_type),
    data: rowsSorted,
  });
  Vue.set(state.datasets[key], 'column', {
    labels: colsSorted.map(c => c.column_type),
    data: colsSorted,
  });
}

/*
 * Private action helpers
 */
export async function load_dataset({ commit }, { dataset_id, selected }) {
  try {
    const { data } = await CSVService.get(dataset_id);
    commit(SET_SOURCE_DATA, { data: { ...data, selected } });
    await CSVService.validateTable(dataset_id);
  } catch (err) {
    commit(SET_LAST_ERROR, err);
    throw err;
  }
}

const mutations = {

  [SET_SOURCE_DATA](state, { data }) {
    const { id, name, size } = data;
    if (!state.plots[id]) {
      Vue.set(state.plots, id, cloneDeep(plotDefaults));
    }
    if (!state.analyses[id]) {
      Vue.set(state.analyses, id, cloneDeep(analysisDefaults));
    }
    const cols = data.columns.sort((a, b) => a.column_index - b.column_index);
    // serialize CSV string as JSON
    const { data: sourcerows } = convertCsvToRows(data.table);
    Vue.set(state.datasets, id, {
      // API response from server
      _source: data,
      id,
      name,
      size,
      ready: true,
      width: sourcerows[0].length, // TODO: get from server
      height: sourcerows.length, // TODO: get from server
      // user- and server-generated lables for rows and columns
      validation: mapValidationErrors(data.table_validation, cols),
      selected: data.selected || {
        type: 'column',
        last: 1,
        ranges: new RangeList([1]),
      },
      // JSON serialized copy of data.table
      sourcerows,
      // most recent copy of data with all transforms applied.
      transformed: data,
      // mutually exclusive transformation categories
      normalization: data.normalization,
      normalization_argument: data.normalization_argument,
      transformation: data.transformation,
      transformation_argument: null,
      scaling: data.scaling,
      scaling_argument: null,
      imputationMCAR: data.imputation_mcar,
      imputationMNAR: data.imputation_mnar,
    });
    _setLables(state, {
      key: id,
      rows: data.rows,
      columns: data.columns,
    });
  },

  [SET_LABELS](state, { key, rows, columns }) {
    _setLables(state, { key, rows, columns });
  },

  [SET_DATASET](state, { dataset }) {
    Vue.set(state.datasets, dataset.id, dataset);
    if (!state.plots[dataset.id]) {
      Vue.set(state.plots, dataset.id, cloneDeep(plotDefaults));
    }
    if (!state.analyses[dataset.id]) {
      Vue.set(state.analyses, dataset.id, cloneDeep(analysisDefaults));
    }
  },

  [SET_ANALYSIS_OPTIONS](state, { dataset_id, name, options }) {
    Vue.set(state.analyses[dataset_id][name], 'options', options);
  },

  [SET_ANALYSIS_DATA](state, { dataset_id, name, data }) {
    Vue.set(state.analyses[dataset_id][name], 'data', data);
  },

  [SET_ANALYSIS_STATE](state, { dataset_id, name, state: status }) {
    Vue.set(state.analyses[dataset_id][name], 'state', status);
  },

  [REFRESH_PLOT](state, { key, name, data }) {
    Vue.set(state.plots[key][name], 'data', data);
    Vue.set(state.plots[key][name], 'valid', true);
  },

  [REMOVE_DATASET](state, { key }) {
    Vue.delete(state.datasets, key);
    state.store.save(state, state.session_id);
  },

  [SET_LAST_ERROR](state, { err }) {
    Vue.set(state, 'lasterror', err);
  },

  [SET_LOADING](state, loading) {
    Vue.set(state, 'loading', loading);
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

  [SET_SESSION_STORE](state, { store, session_id }) {
    Vue.set(state, 'store', store);
    Vue.set(state, 'session_id', session_id);
  },

  [SET_TRANSFORMATION](state, {
    key, data, transform_type, category, argument,
  }) {
    _invalidatePlots(state, { key, plotList: ['pca', 'loadings'] });
    Vue.set(state.datasets[key], category, transform_type);
    Vue.set(state.datasets[key], `${category}_argument`, argument);
    Vue.set(state.datasets[key], 'transformed', data);
  },
};

const actions = {

  async [UPLOAD_CSV]({ state, commit }, { file }) {
    commit(SET_LOADING, true);
    try {
      const { data } = await CSVService.upload(file);
      commit(SET_SOURCE_DATA, { data });
      state.store.save(state, state.session_id);
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [LOAD_PLOT]({ commit }, { dataset_id, name, max_components }) {
    try {
      const { data } = await CSVService.getPlot(dataset_id, name, {
        max_components,
      });
      commit(REFRESH_PLOT, { key: dataset_id, name, data });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      throw err;
    }
  },

  /**
   * Load datasets from session into the store.
   * @param {Object} vuex
   * @param {import('../utils').SessionStore} sessionStore Store
   */
  async [LOAD_SESSION]({ commit }, store, session_id = 'default') {
    commit(SET_LOADING, true);
    commit(SET_SESSION_STORE, { store, session_id });
    try {
      const { datasets } = store.load(session_id);
      await Promise.all(Object.keys(datasets).map((dataset_id) => {
        const dataset = datasets[dataset_id];
        commit(SET_DATASET, { dataset });
        return load_dataset({ commit }, { dataset_id: dataset.id });
      }));
      commit(SET_LOADING, false);
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
  },

  // set mutually exclusive transformation within category.
  async [MUTEX_TRANSFORM_TABLE]({ commit }, {
    category, dataset_id, transform_type, argument,
  }) {
    const key = dataset_id;
    commit(SET_LOADING, true);
    try {
      const { data } = await CSVService.setTransform(key, category, transform_type, argument);
      commit(SET_TRANSFORMATION, {
        key, data, transform_type, category, argument,
      });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [CHANGE_AXIS_LABEL]({ state, commit }, { dataset_id, changes }) {
    commit(SET_LOADING, true);
    try {
      const { data } = await CSVService.updateLabel(dataset_id, changes);
      const { rows, columns } = data;
      commit(SET_LABELS, { key: dataset_id, rows, columns });
      const { selected } = state.datasets[dataset_id];
      load_dataset({ commit }, { dataset_id, selected });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [CHANGE_IMPUTATION_OPTIONS]({ commit }, { dataset_id, options }) {
    commit(SET_LOADING, true);
    await CSVService.setImputation(dataset_id, options);
    await load_dataset({ commit }, { dataset_id });
    commit(SET_LOADING, false);
  },

  async [CHANGE_ANALYSIS_OPTIONS]({ state, commit }, { dataset_id, name, changes }) {
    commit(SET_ANALYSIS_STATE, { dataset_id, name, state: 'computing' });
    try {
      // create full options
      const options = {
        ...state.analyses[dataset_id][name].options,
        ...changes,
      };
      commit(SET_ANALYSIS_OPTIONS, { dataset_id, name, options });
      const { data } = await CSVService.getAnalysis(dataset_id, name, options);
      commit(SET_ANALYSIS_DATA, { dataset_id, name, data });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_ANALYSIS_STATE, { dataset_id, name, state: 'error' });
      throw err;
    }
    commit(SET_ANALYSIS_STATE, { dataset_id, name, state: 'ready' });
  },
};

export default new Vuex.Store({
  state: appstate,
  getters,
  mutations,
  actions,
});

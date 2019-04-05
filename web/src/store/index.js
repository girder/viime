import Vue from 'vue';
import Vuex from 'vuex';

import { convertCsvToRows } from '../utils';
import { CSVService } from '../common/api.service';

import {
  CHANGE_AXIS_LABEL,
  MUTEX_TRANSFORM_TABLE,
  LOAD_DATASET,
  LOAD_PLOT,
  UPLOAD_CSV,
} from './actions.type';

import {
  ADD_SOURCE_DATA,
  REFRESH_PLOT,
  SET_TRANSFORMATION,
  SET_LAST_ERROR,
  SET_LOADING,
} from './mutations.type';

Vue.use(Vuex);

const appstate = {
  // map of all datasets in the session by csv UUID
  datasets: {},
  lasterror: null,
  loading: false,
};

const getters = {
  dataset: state => id => state.datasets[id],
  txType: state => (id, category) => state.datasets[id] && state.datasets[id][category],
  plotData: state => (id, name) => state.datasets[id] && state.datasets[id].plots[name].data,
  plotValid: state => (id, name) => state.datasets[id] && state.datasets[id].plots[name].valid,
};


/*
 * Private mutation helpers
 */
function _invalidatePlots(state, { key, plotList }) {
  plotList.forEach((name) => {
    Vue.set(state.datasets[key].plots[name], 'valid', false);
  });
}

const mutations = {

  [ADD_SOURCE_DATA](state, { data, visible }) {
    const key = data.id;
    // Server doesn't guarantee order of indices.
    const rows = data.rows.sort((a, b) => a.row_index - b.row_index);
    const cols = data.columns.sort((a, b) => a.column_index - b.column_index);
    // serialize CSV string as JSON
    const { data: sourcerows } = convertCsvToRows(data.table);

    Vue.set(state.datasets, key, {
      // API response from server
      source: data,
      visible,
      width: sourcerows[0].length, // TODO: get from server
      height: sourcerows.length, // TODO: get from server
      // user- and server-generated lables for rows and columns
      row: {
        labels: rows.map(r => r.row_type),
      },
      column: {
        labels: cols.map(c => c.column_type),
      },
      validation: [
        {
          severity: 'error', type: 'primary-key', title: 'Primary key missing', description: 'Please ensure the column has a primary key',
        },
        {
          severity: 'error', type: 'group-tag', title: 'Group tag missing', description: 'Please ensure the column has a group',
        },
        {
          severity: 'error',
          type: 'missing-data',
          title: 'Missing data',
          data: [
            { index: 3, info: '43% missing' },
            { index: 6, info: '23% missing' },
            { index: 8, info: '53% missing' },
            { index: 11, info: '12% missing' },
            { index: 13, info: '43% missing' },
            { index: 18, info: '42% missing' },
            { index: 22, info: '51% missing' },
            { index: 25, info: '14% missing' },
            { index: 26, info: '10% missing' },
            { index: 27, info: '13% missing' },
          ],
        },
        {
          severity: 'warning',
          type: 'low-variance',
          title: 'Low variance',
          data: [
            { index: 30, info: 'r² .08' },
            { index: 33, info: 'r² .15' },
            { index: 34, info: 'r² 1.5' },
            { index: 35, info: 'r² 1.1' },
            { index: 36, info: 'r² .05' },
            { index: 38, info: 'r² .06' },
          ],
        },
      ],
      // JSON serialized copy of data.table
      sourcerows,
      // most recent copy of data with all transforms applied.
      transformed: data,
      // mutually exclusive transformation categories
      normalization: data.normalization,
      transformation: null, // TODO: add
      scaling: null, // TODO: add
      // data for visualizations
      plots: {
        // logic for which mutations invalidate plot data cache is internal to vuex state
        // this could be more granular.  for now, mutations invalidate all plots.
        // enumerate plot types
        pca: {
          data: null,
          valid: false,
        },
      },
    });
  },


  [REFRESH_PLOT](state, { key, name, data }) {
    Vue.set(state.datasets[key].plots[name], 'data', data);
    Vue.set(state.datasets[key].plots[name], 'valid', true);
  },

  [SET_LAST_ERROR](state, { err }) {
    Vue.set(state, 'lasterror', err);
  },

  [SET_TRANSFORMATION](state, {
    key, data, transform_type, category,
  }) {
    _invalidatePlots(state, { key, plotList: ['pca'] });
    Vue.set(state.datasets[key], category, transform_type);
    Vue.set(state.datasets[key], 'transformed', data);
  },

  [SET_LOADING](state, loading) {
    Vue.set(state, 'loading', loading);
  },
};

const actions = {
  async [UPLOAD_CSV]({ commit }, { file, visible }) {
    const formData = new FormData();
    formData.append('file', file);
    commit(SET_LOADING, true);
    try {
      const { data } = await CSVService.upload(formData);
      commit(ADD_SOURCE_DATA, { data, visible });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [LOAD_DATASET]({ commit }, { dataset_id }) {
    try {
      const { data } = await CSVService.get(dataset_id);
      commit(ADD_SOURCE_DATA, { data, visible: true });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      throw err;
    }
  },

  // set mutually exclusive transformation within category.
  async [MUTEX_TRANSFORM_TABLE]({ commit }, {
    category, dataset_id, transform_type,
  }) {
    const key = dataset_id;
    commit(SET_LOADING, true);
    try {
      const { data } = await CSVService.setTransform(key, category, transform_type);
      commit(SET_TRANSFORMATION, {
        key, data, transform_type, category,
      });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [CHANGE_AXIS_LABEL]({ commit }, { dataset_id, changes }) {
    commit(SET_LOADING, true);
    try {
      const { data } = await CSVService.updateLabel(dataset_id, changes);
      commit(ADD_SOURCE_DATA, { data, visible: true });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [LOAD_PLOT]({ commit }, { dataset_id, name }) {
    try {
      const { data } = await CSVService.getPlot(dataset_id, name);
      commit(REFRESH_PLOT, { key: dataset_id, name, data });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
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

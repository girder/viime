import Vue from 'vue';
import Vuex from 'vuex';

import { convertCsvToRows } from '../utils';
import { CSVService } from '../common/api.service';

import {
  defaultRowOption,
  defaultColOption,
  rowPrimaryKey,
  colPrimaryKey,
} from '../utils/constants';

import {
  CHANGE_AXIS_LABEL,
  UPLOAD_CSV,
  MUTEX_TRANSFORM_TABLE,
  LOAD_DATASET,
} from './actions.type';

import {
  ADD_SOURCE_DATA,
  SET_AXIS_LABEL,
  SET_TRANSFORMATION,
  SET_TRANSFORM_DATA,
  SET_LAST_ERROR,
  SET_LOADING,
} from './mutations.type';

Vue.use(Vuex);

/**
 * Dataset schema
 * @typedef {Object} Dataset
 * @property {Array} source the unaltered source data
 * @property {Number} width raw width
 * @property {Number} height raw height
 * @property {Array} transformed the most recent transform data
 * @property {Array} transformations a list of all transformations on the dataset
 * @property {String} normalization there can only be 1.
 */

const appstate = {
  // map of all datasets in the session by csv UUID
  datasets: {},
  lasterror: null,
  loading: false,
};

const getters = {
  dataset: state => id => state.datasets[id],
  txType: state => (id, category) => state.datasets[id] && state.datasets[id][category],
};

const mutations = {

  [ADD_SOURCE_DATA](state, { data, visible }) {
    const key = data.id;

    // Server doesn't guarantee order of indices.
    const rows = data.rows.sort((a, b) => a.row_index - b.row_index);
    const row_key_index = rows.find(r => r.row_type === rowPrimaryKey);
    const cols = data.columns.sort((a, b) => a.column_index - b.column_index);
    const col_key_index = cols.find(c => c.column_type === colPrimaryKey);

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
        primary_key: row_key_index ? row_key_index.row_index : null,
      },
      column: {
        labels: cols.map(c => c.column_type),
        primary_key: col_key_index ? col_key_index.column_index : null,
      },
      // JSON serialized copy of data.table
      sourcerows,
      // most recent copy of data with all transforms applied.
      transformed: data,
      // mutually exclusive transformation categories
      normalization: data.normalization,
      transformation: null, // TODO: add
      scaling: null, // TODO: add
    });
  },

  [SET_AXIS_LABEL](state, {
    key, axis_name, index, value, isPrimary,
  }) {
    Vue.set(state.datasets[key][axis_name].labels, index, value);
    const oldprimary = state.datasets[key][axis_name].primary_key;

    let default_axis_label = null;
    if (axis_name === 'row') {
      default_axis_label = defaultRowOption;
    } else if (axis_name === 'column') {
      default_axis_label = defaultColOption;
    }

    if (isPrimary) {
      if (oldprimary !== null) {
        Vue.set(state.datasets[key][axis_name].labels, oldprimary, default_axis_label);
      }
      Vue.set(state.datasets[key][axis_name], 'primary_key', index);
    } else if (index === oldprimary) {
      Vue.set(state.datasets[key][axis_name], 'primary_key', null);
    }
  },

  [SET_LAST_ERROR](state, { err }) {
    Vue.set(state, 'lasterror', err);
  },

  [SET_TRANSFORM_DATA](state, { data }) {
    const key = data.id;
    Vue.set(state.datasets[key], 'transformed', data);
  },

  [SET_TRANSFORMATION](state, { key, data, category }) {
    Vue.set(state.datasets[key], category, data);
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
      commit(SET_TRANSFORMATION, { key, data: transform_type, category });
      commit(SET_TRANSFORM_DATA, { data });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },

  async [CHANGE_AXIS_LABEL]({ commit }, {
    dataset_id, axis_name, label, index,
  }) {
    const params = {};
    commit(SET_LOADING, true);
    params[`${axis_name}_type`] = label;
    try {
      await CSVService.updateAxis(dataset_id, axis_name, index, params);
      commit(SET_AXIS_LABEL, {
        key: dataset_id,
        axis_name,
        index,
        value: label,
        isPrimary: [rowPrimaryKey, colPrimaryKey].indexOf(label) >= 0,
      });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      commit(SET_LOADING, false);
      throw err;
    }
    commit(SET_LOADING, false);
  },
};

export default new Vuex.Store({
  state: appstate,
  getters,
  mutations,
  actions,
});

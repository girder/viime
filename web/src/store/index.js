import Vue from 'vue';
import Vuex from 'vuex';

import { convertCsvToRows } from '../utils/trash';
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
} from './actions.type';

import {
  ADD_SOURCE_DATA,
  REMOVE_TRANSFORMATION,
  SET_AXIS_LABEL,
  SET_TRANSFORMATION,
  SET_TRANSFORM_DATA,
  SET_LAST_ERROR,
} from './mutations.type';

Vue.use(Vuex);

/**
 * Dataset schema
 * @typedef {Object} Dataset
 * @property {Array} source the unaltered source data
 * @property {Array} transformed the most recent transform data
 * @property {Array} transformations a list of all transformations on the dataset
 * @property {String} normalization there can only be 1.
 */

const state = {
  // map of all datasets in the session by csv UUID
  datasets: {},
  lasterror: null,
};

const getters = {
  dataset: (state) => (id) => state.datasets[id],
};

const mutations = {

  [ADD_SOURCE_DATA](state, { data }) {
    const key = data.id;
    
    const rows = Array(data.rows.length).fill();
    data.rows.forEach((r) => {
      rows[r.row_index] = r;
    });
    const cols = Array(data.columns.length).fill();
    data.columns.forEach((c) => {
      cols[c.column_index] = c;
    });
    
    const { data: sourcerows } = convertCsvToRows(data.table);
    Vue.set(state.datasets, key, {
      // API response from 
      source: data,
      width: sourcerows[0].length, // TODO: get from server
      height: sourcerows.length, // TODO: get from server
      // user- and server-generated lables for rows and columns
      row: {
        labels: rows.map(r => r.row_type),
        primary_key: 0,
      },
      column: {
        labels: cols.map(c => c.column_type),
        primary_key: 0,
      },
      // JSON serialized copy of data.table
      sourcerows,
      // most recent copy of data with all transforms applied.
      transformed: data,
      // full map of all transformations on source
      transformations: {},
      // mutually exclusive transformation categories
      // if SET_TRANSFORMATION is called for one of these names,
      // the current transform is deleted and replaced with the new one.
      normalization: null,
      transformation: null,
      scaling: null,
    });
  },

  [REMOVE_TRANSFORMATION](state, { key, tx_key, category }) {
    if (category) {
      state.datasets[key][category] = null;
    }
    delete state.datasets[key].transformations[tx_key];
  },

  [SET_AXIS_LABEL](state, { key, axis, index, value, isPrimary }) {
    Vue.set(state.datasets[key][axis].labels, index, value);
    const oldprimary = state.datasets[key][axis].primary_key;
    const default_axis_label = axis === 'col' ? defaultColOption : defaultRowOption;
    if (isPrimary) {
      if (oldprimary !== null) {
        Vue.set(state.datasets[key][axis].labels, oldprimary, default_axis_label);
      }
      Vue.set(state.datasets[key][axis], 'primary_key', index);
    } else if (index === oldprimary) {
      Vue.set(state.datasets[key][axis], 'primary_key', null);
    }
  },

  [SET_LAST_ERROR](state, { err }) {
    state.lasterror = err;
  },

  [SET_TRANSFORM_DATA](state, { data }) {
    const key = data.id;
    state.datasets[key].transformed = data;
  },

  [SET_TRANSFORMATION](state, { key, data, category }) {
    const tx_key = data.id;
    if (category) {
      state.datasets[key][category] = data;
    }
    state.datasets[key].transformations[tx_key] = data;
  },

};

const actions = {
  async [UPLOAD_CSV]({ commit }, { file }) {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const { data } = await CSVService.upload(formData);
      commit(ADD_SOURCE_DATA, { data });
    } catch (err){
      commit(SET_LAST_ERROR, err);
      throw err;
    }
  },

  // set mutually exclusive transformation within category.
  async [MUTEX_TRANSFORM_TABLE]({state, commit}, { category, dataset_id, transform_type, args }) {
    const key = dataset_id;
    const last = state.datasets[key][category];
    if (transform_type === null || last) {
      // remove the existing transform
      try {
        await CSVService.dropTransform(key, last.id);
        if (last) commit(REMOVE_TRANSFORMATION, { key, tx_key: last.id, category });
      } catch (err){
        commit(SET_LAST_ERROR, err);
        throw err;
      }
    }
    if (transform_type !== null) {
      // create new transform
      try {
        const { data } = await CSVService.addTransform(key, { transform_type, args });
        commit(SET_TRANSFORMATION, { key, data, category });
      } catch (err){
        commit(SET_LAST_ERROR, err);
        throw err;
      }
    }

    try {
      const { data } = await CSVService.get(key);
      commit(SET_TRANSFORM_DATA, { data });
    } catch (err){
      commit(SET_LAST_ERROR, err);
      throw err;
    }
  },
  
  async [CHANGE_AXIS_LABEL]({commit}, { dataset_id, axis, label, index }) {
    const params = {};
    params[`${axis}_type`] = label;

    try {
      await CSVService.updateAxis(dataset_id, axis, index, params);
      commit(SET_AXIS_LABEL, {
        key: dataset_id,
        axis,
        index,
        value: label,
        isPrimary: [rowPrimaryKey, colPrimaryKey].indexOf(label) >= 0,
      });
    } catch (err) {
      commit(SET_LAST_ERROR, err);
      throw err;
    }
  },
};

export default new Vuex.Store({
  state,
  getters,
  mutations,
  actions
});

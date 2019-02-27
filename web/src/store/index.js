import Vue from 'vue';
import Vuex from 'vuex';

import { convertCsvToRows } from '../utils/trash';
import { CSVService } from '../common/api.service';

import {
  UPLOAD_CSV,
  MUTEX_TRANSFORM_TABLE,
} from './actions.type';

import {
  ADD_SOURCE_DATA,
  REMOVE_TRANSFORMATION,
  SET_TRANSFORMATION,
  SET_TRANSFORM_DATA,
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
  datasets: {},
};

const getters = {};

const mutations = {
  [ADD_SOURCE_DATA](state, { data }) {
    const key = data.id;
    Vue.set(state.datasets, key, {
      source: data,
      sourcerows: convertCsvToRows(data.table),
      transformed: data,
      transformations: {},
      // mutually exclusive transformation categories.
      normalization: null,
      transformation: null,
      scaling: null,
    });
  },
  [SET_TRANSFORM_DATA](state, { data }) {
    const key = data.id;
    state.datasets[key].transformed = data;
  },
  [REMOVE_TRANSFORMATION](state, { key, tx_key, category }) {
    if (category) {
      state.datasets[key][category] = null;
    }
    delete state.datasets[key].transformations[tx_key];
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
    const { data } = await CSVService.upload(formData);
    commit(ADD_SOURCE_DATA, { data });
  },

  // set mutually exclusive transformation within category.
  async [MUTEX_TRANSFORM_TABLE]({state, commit}, { category, dataset_id, transform_type, args }) {
    const key = dataset_id;
    const last = state.datasets[key][category];
    if (transform_type === null || last) {
      // remove the existing transform
      await CSVService.dropTransform(key, last.id);
      if (last) commit(REMOVE_TRANSFORMATION, { key, tx_key: last.id, category });
    }
    if (transform_type !== null) {
      // create new transform
      const { data } = await CSVService.addTransform(key, { transform_type, args });
      commit(SET_TRANSFORMATION, { key, data, category });
    }
    const { data } = await CSVService.get(key);
    commit(SET_TRANSFORM_DATA, { data });
  },
};

export default new Vuex.Store({
  state,
  getters,
  mutations,
  actions
});

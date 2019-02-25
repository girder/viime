import Vue from 'vue';
import Vuex from 'vuex';

import { CSVService } from '../common/api.service';

import { UPLOAD_CSV, NORMALIZE_TABLE } from './actions.type';
import { ADD_SOURCE_DATA, SET_TRANSFORM_DATA } from './mutations.type';

Vue.use(Vuex);

const state = {
  sourcedata: null,
  transformdata: null,
};

const getters = {};

const mutations = {
  [ADD_SOURCE_DATA](state, { data }) {
    state.sourcedata = data;
    state.transformdata = data;
  },
  [SET_TRANSFORM_DATA](state, { data }) {
    state.transformdata = data;
  },
};

const actions = {
  async [UPLOAD_CSV]({ commit }, { file }) {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await CSVService.upload(formData);
    commit(ADD_SOURCE_DATA, { data });
  },

  async [NORMALIZE_TABLE]({state, commit}, { method }) {
    const slug = state.sourcedata.id;
    const { data } = await CSVService.normalize(slug, method);
    commit(SET_TRANSFORM_DATA, data);
  },
};

export default new Vuex.Store({
  state,
  getters,
  mutations,
  actions
});

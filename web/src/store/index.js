import Vue from 'vue';
import Vuex from 'vuex';

import { CSVService } from '../common/api.service';

import { UPLOAD_CSV } from './actions.type';
import { ADD_SOURCE_DATA } from './mutations.type';

Vue.use(Vuex);

const state = {
  sourcedata: [],
};

const getters = {};

const mutations = {
  [ADD_SOURCE_DATA](state, { data }) {
    state.sourcedata.push(data);
  },
};

const actions = {
  async [UPLOAD_CSV]({ commit }, { file }) {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await CSVService.upload(formData);
    commit(ADD_SOURCE_DATA, { data });
  },
};

export default new Vuex.Store({
  state,
  getters,
  mutations,
  actions
});

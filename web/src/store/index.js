import Vue from 'vue';
import Vuex from 'vuex';

import { CSVService } from '../common/api.service';

import {
  UPLOAD_CSV,
  NORMALIZE_TABLE,
} from './actions.type';

import {
  ADD_SOURCE_DATA,
  CLEAR_NORMALIZATION,
  SET_NORMALIZATION,
  SET_TRANSFORM_DATA,
} from './mutations.type';

Vue.use(Vuex);

const state = {
  sourcedata: null,
  transformdata: null,
  normalizations: [], // should only support 0 or 1 for now.
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
  [SET_NORMALIZATION](state, { data }) {
    state.normalizations.push(data);
  },
  [CLEAR_NORMALIZATION](state){
    state.normalizations = [];
  }
};

const actions = {
  async [UPLOAD_CSV]({ commit }, { file }) {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await CSVService.upload(formData);
    commit(ADD_SOURCE_DATA, { data });
  },

  async [NORMALIZE_TABLE]({state, commit}, { transform_type, args }) {
    const slug = state.sourcedata.id;
    if (transform_type !== null) {
      const { data } = await CSVService.addTransform(slug, { transform_type, args });
      commit(SET_NORMALIZATION, { data });
    } else {
      const promises = state.normalizations.map((n) => {
        return CSVService.dropTransform(slug, n.id);
      })
      await Promise.all(promises);
      commit(CLEAR_NORMALIZATION);
    }
    
    const { data } = await CSVService.get(slug);
    commit(SET_TRANSFORM_DATA, { data });
  },
};

export default new Vuex.Store({
  state,
  getters,
  mutations,
  actions
});

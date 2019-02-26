import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';

const ApiService = {
  init() {
    Vue.use(VueAxios, axios);
    Vue.axios.defaults.baseURL = '/api/v1';
  },

  buildUrl(path) {
    return [Vue.axios.defaults.baseURL, path].join('/');
  },

  get(resource, slug = "") {
    return Vue.axios.get(`${resource}/${slug}`);
  },

  post(resource, data) {
    return Vue.axios.post(resource, data);
  },
  
  put(resource, data) {
    return Vue.axios.put(resource, data);
  },

  delete(resource) {
    return Vue.axios.delete(resource);
  },

  upload(resource, data) {
    return Vue.axios.post(`${resource}/upload`, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  download(resource, slug) {
    return Vue.axios.get(`${resource}/${slug}/download`);
  }
};

export default ApiService;

export const CSVService = {
  
  get(slug) {
    return ApiService.get('csv', slug);
  },

  getChartUrl(slug, type) {
    return ApiService.buildUrl(`csv/${slug}/plot/${type}`);
  },

  post(data) {
    return ApiService.post('csv', data)
  },

  upload(data) {
    return ApiService.upload('csv', data);
  },

  download(slug) {
    return ApiService.download('csv', slug);
  },

  addTransform(slug, { transform_type, args }) {
    return ApiService.post(`csv/${slug}/transform`, { transform_type, ...args });
  },

  dropTransform(csvSlug, transformSlug) {
    return ApiService.delete(`csv/${csvSlug}/transform/${transformSlug}`);
  }
};

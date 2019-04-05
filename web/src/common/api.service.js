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

  get(resource, path, params = {}) {
    return Vue.axios.get(`${resource}/${path}`, { params });
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
  },
};

export default ApiService;

export const CSVService = {

  get(slug) {
    return ApiService.get('csv', slug);
  },

  getPlot(slug, type, params = {}) {
    return ApiService.get('csv', `${slug}/plot/${type}`, params);
  },

  post(data) {
    return ApiService.post('csv', data);
  },

  upload(data) {
    return ApiService.upload('csv', data);
  },

  download(slug) {
    return ApiService.download('csv', slug);
  },

  setTransform(slug, category, transform_type) {
    return ApiService.put(`csv/${slug}/${category}`, { method: transform_type });
  },

  updateLabel(csvSlug, changes) {
    return ApiService.put(`csv/${csvSlug}/batch/label`, { changes });
  },
};

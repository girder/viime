import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';

const ApiService = {
  init() {
    Vue.use(VueAxios, axios);
    Vue.axios.defaults.baseURL = `${process.env.VUE_APP_SERVER_ADDRESS}/api/v1`;
  },

  buildUrl(path, args) {
    const base = [Vue.axios.defaults.baseURL, path].join('/');
    if (!args) {
      return base;
    }
    const params = new URLSearchParams();
    Object.keys(args).forEach((arg) => {
      params.set(arg, String(args[arg]));
    });
    return `${base}?${params.toString()}`;
  },

  list(resource, params = {}) {
    return Vue.axios.get(resource, { params });
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

  merge(data) {
    return Vue.axios.post('merge', data);
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

  getAnalysis(slug, key, params = {}) {
    return ApiService.get('csv', `${slug}/analyses/${key}`, params);
  },

  post(data) {
    return ApiService.post('csv', data);
  },

  upload(file) {
    const formData = new FormData();
    formData.append('file', file);
    return ApiService.upload('csv', formData);
  },

  download(slug) {
    return ApiService.download('csv', slug);
  },

  remerge(slug, params) {
    return ApiService.post(`csv/${slug}/remerge`, params);
  },

  validatedDownloadUrl(slug, args) {
    return ApiService.buildUrl(`csv/${slug}/validate/download`, args);
  },

  setName(slug, name) {
    return ApiService.put(`csv/${slug}/name`, { name });
  },

  setDescription(slug, description) {
    return ApiService.put(`csv/${slug}/description`, { description });
  },

  setGroupLevels(slug, groupLevels) {
    return ApiService.put(`csv/${slug}/group-levels`, { group_levels: groupLevels });
  },

  setSelectedColumns(slug, columns) {
    return ApiService.put(`csv/${slug}/selected-columns`, { columns });
  },

  setTransform(slug, category, transform_type, argument) {
    return ApiService.put(`csv/${slug}/${category}`, { method: transform_type, argument });
  },

  setImputation(slug, methods) {
    return ApiService.put(`csv/${slug}/imputation`, methods);
  },

  updateLabel(csvSlug, changes) {
    return ApiService.put(`csv/${csvSlug}/batch/label`, { changes });
  },

  validateTable(slug) {
    return ApiService.post(`csv/${slug}/validate`);
  },
};


export const ExcelService = {
  upload(file) {
    const formData = new FormData();
    formData.append('file', file);
    return ApiService.upload('excel', formData);
  },
};


export const SampleService = {

  get(slug) {
    return ApiService.get('sample/sample', slug);
  },

  list() {
    return ApiService.list('sample/sample');
  },

  importSample(sampleId) {
    return ApiService.post(`sample/import/${sampleId}`);
  },

  importSampleGroup(group) {
    return ApiService.post(`sample/importgroup/${group}`);
  },
};

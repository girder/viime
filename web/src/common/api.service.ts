import Vue from 'vue';
import axios, { AxiosPromise } from 'axios';
import VueAxios from 'vue-axios';
import { Dictionary } from 'vuex';
import { ISampleFile, ISampleGroup, ILevel } from '../store/model';

const ApiService = {
  init() {
    Vue.use(VueAxios, axios);
    Vue.axios.defaults.baseURL = '/api/v1';
  },

  buildUrl(path: string, args: Dictionary<any>) {
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

  list(resource: string, params: Dictionary<any> = {}) {
    return Vue.axios.get(resource, { params });
  },

  get(resource: string, path: string, params = {}) {
    return Vue.axios.get(`${resource}/${path}`, { params });
  },

  post(resource: string, data: Dictionary<any> = {}) {
    return Vue.axios.post(resource, data);
  },

  put(resource: string, data: Dictionary<any> = {}) {
    return Vue.axios.put(resource, data);
  },

  delete(resource: string) {
    return Vue.axios.delete(resource);
  },

  upload(resource: string, data: FormData | Dictionary<any> = {}) {
    return Vue.axios.post(`${resource}/upload`, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  download(resource: string, slug: string) {
    return Vue.axios.get(`${resource}/${slug}/download`);
  },

  merge(data: FormData | Dictionary<any>) {
    return Vue.axios.post('merge', data);
  },
};

export default ApiService;

export const CSVService = {

  get(slug: string) {
    return ApiService.get('csv', slug);
  },

  getPlot(slug: string, type: string, params = {}) {
    return ApiService.get('csv', `${slug}/plot/${type}`, params);
  },

  getAnalysis(slug: string, key: string, params = {}) {
    return ApiService.get('csv', `${slug}/analyses/${key}`, params);
  },

  post(data: Dictionary<any>) {
    return ApiService.post('csv', data);
  },

  upload(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return ApiService.upload('csv', formData);
  },

  download(slug: string) {
    return ApiService.download('csv', slug);
  },

  remerge(slug: string, params: Dictionary<any>) {
    return ApiService.post(`csv/${slug}/remerge`, params);
  },

  validatedDownloadUrl(slug: string, args: Dictionary<any>) {
    return ApiService.buildUrl(`csv/${slug}/validate/download`, args);
  },

  setName(slug: string, name: string) {
    return ApiService.put(`csv/${slug}/name`, { name });
  },

  setDescription(slug: string, description: string) {
    return ApiService.put(`csv/${slug}/description`, { description });
  },

  setGroupLevels(slug: string, groupLevels: ILevel[]) {
    return ApiService.put(`csv/${slug}/group-levels`, { group_levels: groupLevels });
  },

  setSelectedColumns(slug: string, columns: string[]) {
    return ApiService.put(`csv/${slug}/selected-columns`, { columns });
  },

  setTransform(slug: string, category: string, transform_type: string, argument: any) {
    return ApiService.put(`csv/${slug}/${category}`, { method: transform_type, argument });
  },

  setImputation(slug: string, methods: {mnar: string, mcar: string}) {
    return ApiService.put(`csv/${slug}/imputation`, methods);
  },

  updateLabel(csvSlug: string, changes: {context: string, index: number, label: string}[]) {
    return ApiService.put(`csv/${csvSlug}/batch/label`, { changes });
  },

  validateTable(slug: string) {
    return ApiService.post(`csv/${slug}/validate`);
  },
};


export const ExcelService = {
  upload(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return ApiService.upload('excel', formData);
  },
};


export const SampleService = {

  get(slug: string): AxiosPromise<ISampleFile> {
    return ApiService.get('sample/sample', slug);
  },

  list(): AxiosPromise<ISampleGroup[]> {
    return ApiService.list('sample/sample');
  },

  importSample(sampleId: string) {
    return ApiService.post(`sample/import/${sampleId}`);
  },

  importSampleGroup(group: string) {
    return ApiService.post(`sample/importgroup/${group}`);
  },
};

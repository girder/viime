import Vue from 'vue';
import Router from 'vue-router';

import Upload from '../components/Upload.vue';
import Transform from '../components/Transform.vue';

Vue.use(Router);

export const routes = [
  {
    path: '/select',
    name: 'Upload Data',
    component: Upload,
  },
  {
    path: '/transform',
    name: 'Transform Data',
    component: Transform,
  },
  {
    path: '/',
    redirect: { name: 'Upload Data' },
  },
];

export default new Router({ routes });

import Vue from 'vue';
import Router from 'vue-router';

import Cleanup from '../components/views/Cleanup.vue';
import Upload from '../components/views/Upload.vue';
import Transform from '../components/views/Transform.vue';

Vue.use(Router);

export const routes = [
  {
    path: '/select',
    name: 'Upload Data',
    component: Upload,
  },
  {
    path: '/cleanup/:id',
    name: 'Cleanup Data',
    component: Cleanup,
  },
  {
    path: '/transform/:id',
    name: 'Transform Data',
    component: Transform,
  },
  {
    path: '/',
    redirect: { name: 'Upload Data' },
  },
];

export default new Router({ routes });

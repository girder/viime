import Vue from 'vue';
import Router from 'vue-router';

import Pretreatment from '../components/Pretreatment.vue';
import Cleanup from '../components/Cleanup.vue';
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
    path: '/pretreatment/:id',
    name: 'Pretreat Data',
    component: Pretreatment,
    children: [
      {
        path: 'cleanup',
        name: 'Cleanup Data',
        component: Cleanup,
      },
      {
        path: 'transform',
        name: 'Transform Data',
        component: Transform,
      },
    ],
  },
  {
    path: '/',
    redirect: { name: 'Upload Data' },
  },
];

export default new Router({ routes });

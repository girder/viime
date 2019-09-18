import Vue from 'vue';
import Router from 'vue-router';

import Pretreatment from '../components/Pretreatment.vue';
import Cleanup from '../components/Cleanup.vue';
import Upload from '../components/Upload.vue';
import Transform from '../components/Transform.vue';
import ProblemBar from '../components/ProblemBar.vue';

Vue.use(Router);

function injectParams(path, params) {
  let parsed = path;
  Object.entries(params).forEach(([k, v]) => {
    parsed = parsed.replace(`:${k}`, v);
  });
  return parsed;
}

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
    props: true,
    meta: {
      breadcrumb(params, store, isFull) {
        const ds = store.getters.dataset(params.id);
        return {
          text: ds ? ds.name : params.id,
          to: isFull ? this.path : injectParams(this.path, params),
        };
      },
    },
    children: [
      {
        path: 'cleanup',
        name: 'Clean Up Table',
        component: Cleanup,
        props: true,
        children: [
          {
            path: ':problem',
            component: ProblemBar,
            props: true,
          },
        ],
      },
      {
        path: 'transform',
        name: 'Transform Table',
        component: Transform,
        props: true,
      },
    ],
  },
  {
    path: '/',
    redirect: { name: 'Upload Data' },
  },
];

export default new Router({ routes });

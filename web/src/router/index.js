import Vue from 'vue';
import Router from 'vue-router';

import Pretreatment from '../components/Pretreatment.vue';
import Cleanup from '../components/Cleanup.vue';
import Upload from '../components/Upload.vue';
import Transform from '../components/Transform.vue';
import AnalyzeData from '../components/AnalyzeData.vue';
import ProblemBar from '../components/ProblemBar.vue';
import DataSource from '../components/DataSource.vue';
import Impute from '../components/Impute.vue';
import analyses from '../components/vis/analyses';

Vue.use(Router);

export const routes = [
  {
    path: '/select',
    name: 'Upload Data',
    component: Upload,
  },
  {
    path: '/pretreatment/:id',
    component: Pretreatment,
    props: true,
    meta: {
      breadcrumb(params, store) {
        const ds = store.getters.dataset(params.id);
        return {
          text: ds ? ds.name : params.id,
        };
      },
    },
    children: [
      {
        path: '',
        name: 'Pretreat Data',
        component: DataSource,
        props: true,
      },
      {
        path: 'cleanup/impute',
        name: 'Impute Table',
        component: Impute,
        props: true,
      },
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
      {
        path: 'analyze',
        name: 'Analyze Data',
        component: AnalyzeData,
        props: true,
      },
      ...analyses.map(({ path, shortName: name, component }) => ({
        path: `analyze/${path}`, name, component, props: true,
      })),
    ],
  },
  {
    path: '/',
    name: 'Root',
    redirect: { name: 'Upload Data' },
  },
];

export default new Router({ routes });

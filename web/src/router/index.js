import Vue from 'vue';
import Router from 'vue-router';

import Pretreatment from '../components/Pretreatment.vue';
import Cleanup from '../components/Cleanup.vue';
import Upload from '../components/Upload.vue';
import Transform from '../components/Transform.vue';
import Analyze from '../components/analyze/Analyze.vue';
import ProblemBar from '../components/ProblemBar.vue';
import analyses from '../components/analyze';

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
    props: true,
    children: [
      {
        path: 'cleanup',
        name: 'Cleanup Data',
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
        name: 'Transform Data',
        component: Transform,
        props: true,
      },
      {
        path: 'analyze',
        name: 'Analyze Data',
        component: Analyze,
        props: true,
      },
      ...analyses.map(({ path, shortName: name, component }) => ({
        path: `analyze/${path}`, name, component, props: true,
      })),
    ],
  },
  {
    path: '/',
    redirect: { name: 'Upload Data' },
  },
];

export default new Router({ routes });

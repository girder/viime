import Vue from 'vue';
import Router from 'vue-router';

import Pretreatment from '../components/Pretreatment.vue';
import Cleanup from '../components/Cleanup.vue';
import Landing from '../components/Landing.vue';
import ViimeApp from '../components/ViimeApp.vue';
import Upload from '../components/Upload.vue';
import Transform from '../components/Transform.vue';
import AnalyzeData from '../components/AnalyzeData.vue';
import ProblemBar from '../components/ProblemBar.vue';
import DataSource from '../components/DataSource.vue';
import Impute from '../components/Impute.vue';
import Download from '../components/Download.vue';
import NewMerge from '../components/NewMerge.vue';
import RouterView from '../components/RouterView.vue';
import analyses from '../components/vis/analyses';

Vue.use(Router);

export const routes = [
  {
    path: '/app',
    name: 'App',
    component: ViimeApp,
    redirect: { name: 'Upload Data' },
    children: [
      {
        path: 'select',
        name: 'Upload Data',
        component: Upload,
      },
      {
        path: 'try',
        name: 'Try Data',
        component: Upload,
        meta: {
          try: true,
        },
      },
      {
        path: 'pretreatment/merge',
        component: NewMerge,
        name: 'Merge Data',
        props: true,
      },
      {
        path: 'pretreatment/:id',
        component: Pretreatment,
        props: true,
        meta: {
          breadcrumb(params, store) {
            const ds = store.getters.dataset(params.id);
            return {
              text: ds ? ds.name : params.id,
              to: { name: 'Pretreat Data', params },
            };
          },
        },
        children: [
          {
            path: '',
            name: 'Pretreat Data',
            component: DataSource,
            props: true,
            meta: {
              hidden: true,
            },
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
                name: 'Problem',
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
            component: RouterView,
            props: true,
            meta: {
              breadcrumb(params) {
                return {
                  text: 'Analyze Data',
                  to: { name: 'Analyze Data', params },
                };
              },
            },
            children: [
              {
                path: '',
                name: 'Analyze Data',
                component: AnalyzeData,
                props: true,
                meta: {
                  hidden: true,
                },
              },
              ...analyses.map(({ path, shortName: name, component }) => ({
                path, name, component, props: true,
              })),
            ],
          },
          {
            path: 'download',
            name: 'Download Data',
            component: Download,
            props: true,
          },
        ],
      },
    ],
  },
  {
    path: '/',
    name: 'Root',
    component: Landing,
  },
];

export default new Router({ routes });

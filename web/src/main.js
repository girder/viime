import '@mdi/font/css/materialdesignicons.min.css';

import Vue from 'vue';
import Vuetify from 'vuetify';
import * as Sentry from '@sentry/browser';
import { Vue as SentryVue } from '@sentry/integrations';

import ApiService from './common/api.service';
import App from './App.vue';
import router from './router';
import store from './store';
import './stylus/main.styl';
import vuetifyConfig from './utils/vuetifyConfig';

Vue.use(Vuetify, vuetifyConfig);
Vue.config.productionTip = false;

ApiService.init();

Sentry.init({
  dsn: 'https://9c7281f0dfc5402a953698256bd067e0@sentry.io/1437129',
  integrations: [new SentryVue({ Vue })],
});

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app');

import '@mdi/font/css/materialdesignicons.min.css';

import Vue from 'vue';
import Vuetify from 'vuetify';
import './stylus/main.styl';
import { init as SentryInit } from '@sentry/browser';
import { Vue as SentryVue } from '@sentry/integrations';

import ApiService from './common/api.service';
import App from './App.vue';
import router from './router';
import store from './store';
import { LOAD_SESSION } from './store/actions.type';
import vuetifyConfig from './utils/vuetifyConfig';
import { SessionStore } from './utils';

Vue.use(Vuetify, vuetifyConfig);
Vue.config.productionTip = false;

ApiService.init();
store.dispatch(LOAD_SESSION, new SessionStore(window));

if (process.env.NODE_ENV === 'production') {
  SentryInit({
    dsn: 'https://9c7281f0dfc5402a953698256bd067e0@sentry.io/1437129',
    release: COMMITHASH,
    environment: process.env.NODE_ENV,
    integrations: [new SentryVue({ Vue })],
  });
}

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app');

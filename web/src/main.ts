import '@mdi/font/css/materialdesignicons.min.css';

import Vue from 'vue';
import Vuetify from 'vuetify';
import CompositionApi from '@vue/composition-api';
import './stylus/main.styl';
import { init as SentryInit } from '@sentry/browser';
import { Vue as SentryVue } from '@sentry/integrations';
import VueGtag from 'vue-gtag';

import ApiService from './common/api.service';
import App from './App.vue';
import router from './router';
import store from './store';
import { LOAD_SESSION } from './store/actions.type';
import vuetifyConfig from './utils/vuetifyConfig';
import { SessionStore } from './utils';

Vue.use(Vuetify, vuetifyConfig);
Vue.use(CompositionApi);
Vue.config.productionTip = false;

let serverUrl;

try {
  serverUrl = (new URL('/api/v1', process.env.VUE_APP_SERVER_ADDRESS)).href;
} catch {
  if (process.env.NODE_ENV !== 'production') {
    serverUrl = '/api/v1';
  } else {
    throw new Error('Must set VUE_APP_SERVER_ADDRESS in production');
  }
}

ApiService.init(serverUrl);
store.dispatch(LOAD_SESSION, new SessionStore(window));

if (process.env.CONTEXT === 'production') {
  SentryInit({
    dsn: 'https://8a16de58c96648daa122b63a5db9b404@sentry.io/1814179',
    release: COMMITHASH,
    environment: process.env.NODE_ENV,
    integrations: [new SentryVue({ Vue })],
  });
}

Vue.use(VueGtag, {
  config: { id: process.env.VUE_APP_GOOGLE_ANALYTICS_ID },
  enabled: process.env.NODE_ENV === 'production' && process.env.VUE_APP_GOOGLE_ANALYTICS_ID,
  includes: [{ id: process.env.VUE_APP_GOOGLE_ANALYTICS_ID }],
}, router);

new Vue({
  router,
  store,
  // TODO provide the router to avoid circular imports
  provide: {
    router,
  },
  render: (h) => h(App),
}).$mount('#app');

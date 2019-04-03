import '@mdi/font/css/materialdesignicons.min.css';

import _ from 'lodash';
import Vue from 'vue';
import Vuetify from 'vuetify';
import girderVuetifyConfig from '@girder/components/src/utils/vuetifyConfig';

import ApiService from './common/api.service';
import App from './App.vue';
import router from './router';
import store from './store';
import './stylus/main.styl';
import vuetifyConfig from './utils/vuetifyConfig';

Vue.use(Vuetify, vuetifyConfig);
Vue.config.productionTip = false;

ApiService.init();

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app');

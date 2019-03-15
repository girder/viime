import _ from 'lodash';
import Girder from '@girder/components/src';
import girderVuetifyConfig from '@girder/components/src/utils/vuetifyConfig';
import Vue from 'vue';
import Vuetify from 'vuetify';

import ApiService from './common/api.service';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetifyConfig from './utils/vuetifyConfig';

Vue.use(Girder);
Vue.use(Vuetify, _.merge(girderVuetifyConfig, vuetifyConfig));
Vue.config.productionTip = false;

ApiService.init();

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app');

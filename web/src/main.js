import 'vuetify/dist/vuetify.min.css';
import 'material-design-icons-iconfont/dist/material-design-icons.css'

import Vue from 'vue'
import Vuetify from 'vuetify';
import router from './router';
import App from './App.vue'
import vuetifyConfig from './utils/vuetifyConfig';
import ApiService from './common/api.service';

Vue.config.productionTip = false;
Vue.use(Vuetify, vuetifyConfig); 

ApiService.init();

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')

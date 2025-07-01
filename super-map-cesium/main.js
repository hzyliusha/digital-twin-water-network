import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import router from "./router";
import store from './store'
import 'element-ui/lib/theme-chalk/index.css';
// import  '@supermap/vue-iclient3d-webgl/dist/styles/vue-iclient3d-webgl.min.css';
// import VueiClient from '@supermap/vue-iclient3d-webgl';
import '@/styles/index.scss'
import VueBus from 'vue-bus';

// Vue.use(VueiClient);
Vue.use(VueBus);
Vue.use(ElementUI);

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app')

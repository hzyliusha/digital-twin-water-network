import Vue from 'vue'
import Router from 'vue-router'
Vue.use(Router)
const routes = [
    {
        path: '/',
        component: (resolve) => require([`@/views/home`], resolve),
        hidden: true
      },
]
export default new Router({
    mode: '',
    routes: routes 
})


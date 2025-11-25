import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'
import api from './api/index.js'
import './index.css'

const app = createApp(App)
app.use(router)
app.config.globalProperties.$http = api
app.mount('#app')

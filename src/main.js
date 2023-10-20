// import './assets/main.css'

import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// import axios from 'axios'

import App from './App.vue'
//暗黑模式
import 'element-plus/theme-chalk/dark/css-vars.css'

// createApp(App).mount('#app')
const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')

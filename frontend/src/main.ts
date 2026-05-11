import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { message } from 'ant-design-vue'

import App from './App.vue'
import router from './router'

import Antd from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import 'ant-design-vue/dist/reset.css'
import 'dayjs/locale/zh-cn'
import '@/access'


const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Antd)

// 全局配置 message 显示位置，避开 64px 高的顶部导航栏
message.config({ top: '80px' })

// 全局配置 Ant Design 中文语言
app.provide('locale', zhCN)

app.mount('#app')

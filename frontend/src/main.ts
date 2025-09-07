import { createApp } from 'vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import App from './App.vue'

// 设置dayjs中文语言
dayjs.locale('zh-cn')

const app = createApp(App)
app.use(Antd)
app.mount('#app')

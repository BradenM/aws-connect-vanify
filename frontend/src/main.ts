import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import App from './App.vue'
import './index.css'
import 'primevue/resources/themes/saga-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeflex/primeflex.css'

createApp(App).use(PrimeVue).mount('#app')

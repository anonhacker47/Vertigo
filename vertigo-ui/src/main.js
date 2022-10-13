import { createApp } from "vue";

import axios from 'axios'
import App from "./App.vue";
import { createPinia } from 'pinia'
import router from "./router";
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { plugin, defaultConfig } from '@formkit/vue';
import '@formkit/themes/genesis';
import 'animate.css'

import "./assets/main.css";
import Api from "./services/Api";

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate)


app.use(pinia)
app.use(router);
app.use(plugin,defaultConfig);
app.mount("#app");


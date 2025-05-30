import 'animate.css'
import './index.css'
import "./assets/main.css";
import 'swiper/css';
import 'swiper/css/effect-cards';
import 'swiper/css/navigation';


import { createApp } from "vue";
import App from "./App.vue";
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { plugin, defaultConfig } from '@formkit/vue';
import PrimeVue from 'primevue/config';
import '@formkit/themes/genesis';
import ConfirmDialog from 'primevue/confirmdialog'
import Lara from '@primevue/themes/lara';
import { definePreset } from '@primevue/themes';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';
import Toast from "primevue/toast";
import router from "./router";

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate)

const MyPreset = definePreset(Lara, {
    semantic: {
        colorScheme: {
            light: {
                surface: {
                    0: '#ffffff',
                    50: '{zinc.50}',
                    100: '{zinc.100}',
                    200: '{zinc.200}',
                    300: '{zinc.300}',
                    400: '{zinc.400}',
                    500: '{zinc.500}',
                    600: '{zinc.600}',
                    700: '{zinc.700}',
                    800: '{zinc.800}',
                    900: '{zinc.900}',
                    950: '{zinc.950}'
                }
            },
            dark: {
                surface: {
                    0: '#ffffff',
                    50: '{slate.50}',
                    100: '{slate.100}',
                    200: '{slate.200}',
                    300: '{slate.300}',
                    400: '{slate.400}',
                    500: '{slate.500}',
                    600: '{slate.600}',
                    700: '{slate.700}',
                    800: '{slate.800}',
                    900: '{slate.900}',
                    950: '{slate.950}'
                }
            }
        }
    }
});

app.use(router);
app.use(pinia)
app.use(plugin, defaultConfig);
app.use(PrimeVue, {
    // unstyled: true,
    theme: {
        preset: MyPreset
    }
    // pt: Aura
});
app.use(ConfirmationService);
app.use(ToastService);
app.component('ConfirmDialog',ConfirmDialog)
app.component('NotificationToast',Toast)
app.mount("#app");


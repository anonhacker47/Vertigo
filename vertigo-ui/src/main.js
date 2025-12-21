import "animate.css";
import "./assets/main.css";
import "./index.css";
import "swiper/css";
import "swiper/css/effect-cards";
import "swiper/css/navigation";

import { createApp } from "vue";
import App from "./App.vue";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import PrimeVue from "primevue/config";
import ConfirmDialog from "primevue/confirmdialog";
import Lara from "@primevue/themes/lara";
import { definePreset } from "@primevue/themes";
import ConfirmationService from "primevue/confirmationservice";
import ToastService from "primevue/toastservice";
import Toast from "primevue/toast";
import router from "./router";
import Drawer from "primevue/drawer";
import PanelMenu from "primevue/panelmenu";
import Button from "primevue/button";

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const MyPreset = definePreset(Lara, {
  semantic: {
    colorScheme: {
      dark: {
        surface: {
          0: "#ffffff",
          50: "{slate.50}",
          100: "{slate.100}",
          200: "{slate.200}",
          300: "{slate.300}",
          400: "{slate.400}",
          500: "{slate.500}",
          600: "{slate.600}",
          700: "{slate.700}",
          800: "{slate.800}",
          900: "{slate.900}",
          950: "{slate.950}",
        },
      },
    },
  },
});

app.use(router);
app.use(pinia);
app.use(PrimeVue, {
  // unstyled: true,
  theme: {
    preset: MyPreset,
    options: {
      darkModeSelector: '[data-theme="night"]',
    },
  },
  // pt: Aura
});
app.use(ConfirmationService);
app.use(ToastService);
app.component("ConfirmDialog", ConfirmDialog);
app.component("NotificationToast", Toast);
app.mount("#app");
app.component("Drawer", Drawer);
app.component("PanelMenu", PanelMenu);
app.component("Button", Button);

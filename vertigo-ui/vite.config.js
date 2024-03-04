import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "src": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    outDir: "../vertigo-backend/api/wwwroot",
    assetsDir: "static",
  },

  server: {
    host: false
  }   
});
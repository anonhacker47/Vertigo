import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "node:path";
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(),tailwindcss()],
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
      src: fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    outDir: "../vertigo-backend/api/wwwroot",
    assetsDir: "static",
  },
  server: {
    host: true,
    cors: {
      origin: ["http://localhost:5000"],
      credentials: true,
    },
  },
});

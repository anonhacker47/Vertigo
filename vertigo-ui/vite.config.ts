import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';
import tailwindcss from "tailwindcss";

export default defineConfig({
  plugins: [vue()],
  define: {
    '__APP_VERSION__': JSON.stringify(process.env.npm_package_version),
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      'src': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    outDir: '../vertigo-backend/api/wwwroot',
    assetsDir: 'static',
  },
  server: {
    host: false,
  },
  css: {
    postcss: {
      plugins: [tailwindcss()],
    },
  },
});

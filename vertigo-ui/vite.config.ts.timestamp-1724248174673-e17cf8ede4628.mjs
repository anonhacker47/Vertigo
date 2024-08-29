// vite.config.ts
import { fileURLToPath } from "node:url";
import { defineConfig } from "file:///G:/Bilalz/Development/Projects/Full%20stack/flask-vue/Vertigo%20comic%20reader/vertigo-ui/node_modules/vite/dist/node/index.js";
import vue from "file:///G:/Bilalz/Development/Projects/Full%20stack/flask-vue/Vertigo%20comic%20reader/vertigo-ui/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import { resolve } from "path";
import tailwindcss from "file:///G:/Bilalz/Development/Projects/Full%20stack/flask-vue/Vertigo%20comic%20reader/vertigo-ui/node_modules/tailwindcss/lib/index.js";
var __vite_injected_original_dirname = "G:\\Bilalz\\Development\\Projects\\Full stack\\flask-vue\\Vertigo comic reader\\vertigo-ui";
var __vite_injected_original_import_meta_url = "file:///G:/Bilalz/Development/Projects/Full%20stack/flask-vue/Vertigo%20comic%20reader/vertigo-ui/vite.config.ts";
var vite_config_default = defineConfig({
  plugins: [vue()],
  define: {
    "__APP_VERSION__": JSON.stringify(process.env.npm_package_version)
  },
  resolve: {
    alias: {
      "@": resolve(__vite_injected_original_dirname, "./src"),
      "src": fileURLToPath(new URL("./src", __vite_injected_original_import_meta_url))
    }
  },
  build: {
    outDir: "../vertigo-backend/api/wwwroot",
    assetsDir: "static"
  },
  server: {
    host: false
  },
  css: {
    postcss: {
      plugins: [tailwindcss()]
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJHOlxcXFxCaWxhbHpcXFxcRGV2ZWxvcG1lbnRcXFxcUHJvamVjdHNcXFxcRnVsbCBzdGFja1xcXFxmbGFzay12dWVcXFxcVmVydGlnbyBjb21pYyByZWFkZXJcXFxcdmVydGlnby11aVwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiRzpcXFxcQmlsYWx6XFxcXERldmVsb3BtZW50XFxcXFByb2plY3RzXFxcXEZ1bGwgc3RhY2tcXFxcZmxhc2stdnVlXFxcXFZlcnRpZ28gY29taWMgcmVhZGVyXFxcXHZlcnRpZ28tdWlcXFxcdml0ZS5jb25maWcudHNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0c6L0JpbGFsei9EZXZlbG9wbWVudC9Qcm9qZWN0cy9GdWxsJTIwc3RhY2svZmxhc2stdnVlL1ZlcnRpZ28lMjBjb21pYyUyMHJlYWRlci92ZXJ0aWdvLXVpL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZmlsZVVSTFRvUGF0aCB9IGZyb20gJ25vZGU6dXJsJztcclxuaW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSc7XHJcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJztcclxuaW1wb3J0IHsgcmVzb2x2ZSB9IGZyb20gJ3BhdGgnO1xyXG5pbXBvcnQgdGFpbHdpbmRjc3MgZnJvbSBcInRhaWx3aW5kY3NzXCI7XHJcblxyXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoe1xyXG4gIHBsdWdpbnM6IFt2dWUoKV0sXHJcbiAgZGVmaW5lOiB7XHJcbiAgICAnX19BUFBfVkVSU0lPTl9fJzogSlNPTi5zdHJpbmdpZnkocHJvY2Vzcy5lbnYubnBtX3BhY2thZ2VfdmVyc2lvbiksXHJcbiAgfSxcclxuICByZXNvbHZlOiB7XHJcbiAgICBhbGlhczoge1xyXG4gICAgICAnQCc6IHJlc29sdmUoX19kaXJuYW1lLCAnLi9zcmMnKSxcclxuICAgICAgJ3NyYyc6IGZpbGVVUkxUb1BhdGgobmV3IFVSTCgnLi9zcmMnLCBpbXBvcnQubWV0YS51cmwpKSxcclxuICAgIH0sXHJcbiAgfSxcclxuICBidWlsZDoge1xyXG4gICAgb3V0RGlyOiAnLi4vdmVydGlnby1iYWNrZW5kL2FwaS93d3dyb290JyxcclxuICAgIGFzc2V0c0RpcjogJ3N0YXRpYycsXHJcbiAgfSxcclxuICBzZXJ2ZXI6IHtcclxuICAgIGhvc3Q6IGZhbHNlLFxyXG4gIH0sXHJcbiAgY3NzOiB7XHJcbiAgICBwb3N0Y3NzOiB7XHJcbiAgICAgIHBsdWdpbnM6IFt0YWlsd2luZGNzcygpXSxcclxuICAgIH0sXHJcbiAgfSxcclxufSk7XHJcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBaWMsU0FBUyxxQkFBcUI7QUFDL2QsU0FBUyxvQkFBb0I7QUFDN0IsT0FBTyxTQUFTO0FBQ2hCLFNBQVMsZUFBZTtBQUN4QixPQUFPLGlCQUFpQjtBQUp4QixJQUFNLG1DQUFtQztBQUFvUCxJQUFNLDJDQUEyQztBQU05VSxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTLENBQUMsSUFBSSxDQUFDO0FBQUEsRUFDZixRQUFRO0FBQUEsSUFDTixtQkFBbUIsS0FBSyxVQUFVLFFBQVEsSUFBSSxtQkFBbUI7QUFBQSxFQUNuRTtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLE1BQ0wsS0FBSyxRQUFRLGtDQUFXLE9BQU87QUFBQSxNQUMvQixPQUFPLGNBQWMsSUFBSSxJQUFJLFNBQVMsd0NBQWUsQ0FBQztBQUFBLElBQ3hEO0FBQUEsRUFDRjtBQUFBLEVBQ0EsT0FBTztBQUFBLElBQ0wsUUFBUTtBQUFBLElBQ1IsV0FBVztBQUFBLEVBQ2I7QUFBQSxFQUNBLFFBQVE7QUFBQSxJQUNOLE1BQU07QUFBQSxFQUNSO0FBQUEsRUFDQSxLQUFLO0FBQUEsSUFDSCxTQUFTO0FBQUEsTUFDUCxTQUFTLENBQUMsWUFBWSxDQUFDO0FBQUEsSUFDekI7QUFBQSxFQUNGO0FBQ0YsQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K

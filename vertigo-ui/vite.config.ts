import { fileURLToPath } from "node:url";
import { defineConfig, type Plugin } from "vite";
import vue from "@vitejs/plugin-vue";
import { join, resolve } from "node:path";
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { brotliCompressSync, gzipSync } from "node:zlib";
import tailwindcss from '@tailwindcss/vite'

const outDir = resolve(__dirname, "../vertigo-backend/api/wwwroot");

// the backend serves these .gz/.br siblings as they are
const precompress = (): Plugin => ({
  name: "precompress",
  apply: "build",
  closeBundle() {
    for (const entry of readdirSync(outDir, { recursive: true, withFileTypes: true })) {
      if (!entry.isFile() || !/\.(js|css|svg|html|json)$/.test(entry.name)) continue;
      const file = join(entry.parentPath, entry.name);
      const data = readFileSync(file);
      writeFileSync(`${file}.gz`, gzipSync(data, { level: 9 }));
      writeFileSync(`${file}.br`, brotliCompressSync(data));
    }
  },
});

export default defineConfig({
  plugins: [vue(), tailwindcss(), precompress()],
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
      src: fileURLToPath(new URL("./src", import.meta.url)),
      vuedraggable: resolve(__dirname, "node_modules/vuedraggable/src/vuedraggable.js"),
    },
  },
  build: {
    outDir,
    assetsDir: "static",
  },
  server: {
    host: true,
    cors: {
      origin: [],
      credentials: true,
    },
  },
});

<script setup lang="ts">
import { useServerStore } from "@/store/server";

const server = useServerStore();
</script>

<template>
  <div v-if="server.demo" class="demo-ribbon" role="status">
    Demo: read-only. Changes are not saved.
  </div>
</template>

<style scoped>
.demo-ribbon {
  position: fixed;
  inset: auto 0 0 0;
  z-index: 70;
  display: flex;
  align-items: center;
  justify-content: center;
  height: var(--ribbon);
  padding: 0 12px;
  background: #facc15;
  color: #1c1917;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.02em;
  white-space: nowrap;
}
</style>

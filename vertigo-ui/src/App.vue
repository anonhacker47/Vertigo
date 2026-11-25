<script setup lang="ts">
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'
import ConfirmModal from './components/modals/ConfirmModal.vue';
import HeaderItem from "./components/common/HeaderItem.vue";
import DemoRibbon from "./components/common/DemoRibbon.vue";
import { useUserStore } from "./store/user";
import { useServerStore } from "./store/server";
import { onMounted, computed, ref, Ref } from "vue";
import { useRoute } from "vue-router";
import '@/assets/fonts/fonts.css'

const store = useUserStore();
const route = useRoute();

const showNavbar = computed(() => {
  return route.meta.showHeaderItem;
});

const transparentHeader = computed(() => {
  return !!route.meta.transparentHeader;
});

onMounted(() => {
  useServerStore().load();
});
</script>

<template>
  <ErrorBoundary fallback="Something went wrong.">
    <ConfirmModal />
    <div :class="[showNavbar ? 'pt-header' : '']">
      <HeaderItem v-cloak v-if="showNavbar" :transparentHeader="transparentHeader"></HeaderItem>
      <RouterView />
      <NotificationToast position="bottom-center" />
      <DemoRibbon />
    </div>
  </ErrorBoundary>
</template>

<style>
[v-cloak] {
  display: none;
}
</style>

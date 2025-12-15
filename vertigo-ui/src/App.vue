<script setup lang="ts">
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'
import ConfirmDeleteModal from './components/modals/ConfirmDeleteModal.vue';
import HeaderItem from "./components/common/HeaderItem.vue";
import { useUserStore } from "./store/user";
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
});
</script>

<template>
  <ErrorBoundary fallback="Something went wrong.">
    <ConfirmDeleteModal/>
    <div :class="[showNavbar ? 'pt-[72px]' : '']">
      <HeaderItem v-cloak v-if="showNavbar"   :transparentHeader="transparentHeader"></HeaderItem>
      <RouterView />
      <NotificationToast position="bottom-center" />
    </div>
  </ErrorBoundary>
</template>

<style scoped>
[v-cloak] {
  display: none;
}
</style>

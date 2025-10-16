<script setup lang="ts">
import HeaderItem from "./components/HeaderItem.vue";
import { useUserStore } from "./store/user";
import { onMounted, computed, ref, Ref } from "vue";
import { useRoute } from "vue-router";
import '@/assets/fonts/fonts.css'

const store = useUserStore();
const route = useRoute();

const showNavbar = computed(() => {
  return route.meta.showHeaderItem;
});

onMounted(() => {   
});
</script>

<template>
    <HeaderItem v-cloak v-if="showNavbar"></HeaderItem>
    <RouterView />
    <NotificationToast position="bottom-center" />
</template>

<style >
[v-cloak] {
    display: none;
}
</style>

<script setup>
import HeaderItem from "./components/HeaderItem.vue";
import { useUserStore } from "./store/user";
import { onMounted, computed } from "vue";
import { useRoute } from "vue-router";

const store = useUserStore();
const route = useRoute();

const showNavbar = computed(() => route.meta.requiresAuth !== false && !route.meta.removeHeader);

onMounted(() => {
    console.log("App Version:", __APP_VERSION__);
});

</script>

<template>
    <HeaderItem v-cloak v-if="showNavbar"></HeaderItem>
    <RouterView />
</template>

<style >
[v-cloak] {
    display: none;
}
</style>

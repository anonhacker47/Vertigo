<script setup lang="ts">
import HeaderItem from "./components/HeaderItem.vue";
import { useUserStore } from "./store/user";
import { onMounted, computed, ref, Ref } from "vue";
import { useRoute } from "vue-router";

const store = useUserStore();
const route = useRoute();

const showNavbar = computed(() => {
  return route.meta.showHeaderItem;
});

onMounted(() => {   
    // console.log("App Version:", __APP_VERSION__);
    console.log(showNavbar);
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

<script setup>
import HeaderItem from "./components/HeaderItem.vue";
import { useUserStore } from "./store/user";
import { onMounted } from "vue";

const store = useUserStore();

onMounted(() => {
    console.log("App Version:",__APP_VERSION__);
});

</script>

<template>
    <!-- <HeaderItem/> -->
    <RouterView />
</template>

<style scoped></style>

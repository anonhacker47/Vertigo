<script setup>
import HeaderItem from "./components/HeaderItem.vue";
import { useUserStore } from "./store/user";

const store = useUserStore();

</script>

<template>
    <!-- <HeaderItem/> -->
    <RouterView />
</template>

<style scoped></style>

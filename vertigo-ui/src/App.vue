<script setup>
import { useUserStore } from "./store/user";

const store = useUserStore();

</script>

<template>
    <RouterView />
</template>

<style scoped></style>

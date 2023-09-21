<script setup>
import { useUserStore } from "./store/user";
import AuthenticationService from "./services/AuthenticationService";
import { onMounted } from "vue";
const store = useUserStore();

</script>

<template>
    <RouterView />
</template>

<style scoped></style>

<script setup>
import { useUserStore } from "./store/user";
import AuthenticationService from "./services/AuthenticationService";
import { onMounted } from "vue";
const store = useUserStore();
async function refreshToken() {
  const data = {
    access_token: `${store.token}`,
    refresh_token: `${store.refreshtoken}`,
  };
  try {
    const response = await AuthenticationService.refreshToken(data);
    store.token = response.data.access_token;
    store.refreshtoken = response.data.refresh_token;
  } catch (error) {
    console.log(error);
  }
}
</script>

<template>
    <RouterView />
</template>

<style scoped></style>

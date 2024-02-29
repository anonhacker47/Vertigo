<script setup>
import HeaderItem from "./components/HeaderItem.vue";
import { useUserStore } from "./store/user";

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
    <!-- <HeaderItem/> -->
    <RouterView />
</template>

<style scoped></style>

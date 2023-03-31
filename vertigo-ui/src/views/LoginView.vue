<template>
  <div class="flex justify-center items-center h-screen">
    <PanelCardItem>
      <h1
        class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white"
      >
        Sign in to your account
      </h1>
      <FormKit type="form" submit-label="Login" @submit="login">
        <FormKit
          type="text"
          name="username"
          label="Username"
          validation="required"
          label-class="mx-5"
        />
        <FormKit
          type="password"
          name="password"
          label="Password"
          validation="required"
        />
        <h1 v-if="message != ''" class="error py-3">{{ message }}</h1>
      </FormKit>
      <p class="text-sm font-light text-gray-500 dark:text-gray-400">
        Don’t have an account yet?
        <RouterLink to="/register" class="text-blue-500 underline"
          >Sign up</RouterLink
        >
      </p>
    </PanelCardItem>
  </div>
</template>

<script setup>
import { ref } from "vue";
import AuthenticationService from "../services/AuthenticationService";
import { useUserStore } from "../store/user";
import HeaderItem from "../components/HeaderItem.vue";
import PanelCardItem from "../components/cards/PanelCardItem.vue";
import TokenService from "../services/TokenService";
import { useRouter } from "vue-router";

const userStore = useUserStore();
const route = useRouter();
const message = ref("");
const auth = ref();


async function login(values) {
  const encoded_credentials =
    btoa(values.username) + btoa(":" + values.password);

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Basic ${encoded_credentials}`,
  };

  try {
    const response = await AuthenticationService.login({
      headers,
    });
    console.log(response);
    userStore.addToken(response.data.access_token);
    if (localStorage.getItem("token")) {
      const headers = TokenService.getTokenHeader();
      try {
        const response = await AuthenticationService.getUser(
          { headers },);
        userStore.addUser(response.data.id)
      } catch (error) {
        message.value = response;
      }
      route.push("home");
    } else {
      userStore.isUserLoggedIn = false;
    }
  } catch (error) {
    message.value = error;
  }
  console.log(message);
}
</script>

<style scoped>
.formkit-outer {
  color: white;
  outline: none m !important;
}

.formkit-inner {
  background-color: #404a59;
  color: white;
  outline: none m !important;
  box-shadow: 0 0 0 1px #1f2937;
}

[data-type="button"] .formkit-input,
[data-type="submit"] .formkit-input {
  width: 100%;
}
.error {
  color: red;
}
</style>

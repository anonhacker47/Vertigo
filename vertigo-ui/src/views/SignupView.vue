<template>
  <div class="flex justify-center items-center h-screen">
    <PanelCardItem>
      <h1 class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
        Create your Vertigo Account
      </h1>

      <form @submit.prevent="register" class="flex flex-col space-y-4 mt-6">
        <div>
          <label for="username" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Username</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
          />
        </div>

        <div>
          <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Email Address</label>
          <input
            type="email"
            id="email"
            v-model="email"
            required
            placeholder="demo@company.com"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
          />
        </div>

        <div>
          <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
          />
        </div>

        <div>
          <label for="passwordConfirm" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Confirm Password</label>
          <input
            type="password"
            id="passwordConfirm"
            v-model="passwordConfirm"
            required
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
          />
        </div>

        <button
          type="submit"
          class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
        >
          Sign up
        </button>

        <h1 v-if="message" class="error py-5">{{ message }}</h1>
      </form>
      <p class="text-sm font-light text-gray-500 dark:text-gray-400 mt-4">
            Already have an account? 
            <RouterLink to="/login" class="text-blue-500 underline pl-2"> Sign in</RouterLink>
          </p>
    </PanelCardItem>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AuthenticationService from "../services/AuthenticationService";
import PanelCardItem from "../components/cards/PanelCardItem.vue";
import { useRouter } from "vue-router";

const username = ref("");
const email = ref("");
const password = ref("");
const passwordConfirm = ref("");
const message = ref("");

const router = useRouter();

async function register() {
  if (password.value !== passwordConfirm.value) {
    message.value = "Passwords do not match.";
    return;
  }

  try {
    const response = await AuthenticationService.register({
      username: username.value,
      email: email.value,
      password: password.value,
    });
    router.push({ name: "Default" });
  } catch (error) {
    if (error.response?.data) {
      const errData = error.response.data;
      message.value = `Registration failed. ${errData.message}`;
    } else {
      message.value = "Registration failed. Please try again.";
    }
  }
}
</script>

<style>
.error {
  color: red;
}
</style>

<template>
  <div class="relative h-screen flex justify-center items-center overflow-hidden">

    <img src="../assets/logo.svg" alt="Background Logo" class="absolute inset-0 object-cover filter blur-sm opacity-10">

    <PanelCardItem class="relative z-10">
      <h1 class="text-xl font-bold leading-tight tracking-tight text-gray-50 md:text-2xl ">
        Create your Vertigo Account
      </h1>

      <form @submit.prevent="register" class="flex flex-col space-y-4 mt-6">
        <div>
          <label for="username" class="block mb-2 text-sm font-medium text-gray-300">Username</label>
          <input type="text" id="username" v-model="username" required
            class="bg-slate-700 border border-gray-300 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 " />
        </div>

        <div>
          <label for="email" class="block mb-2 text-sm font-medium text-gray-300">Email Address</label>
          <input type="email" id="email" v-model="email" required placeholder="demo@company.com"
            class="bg-slate-700 border border-gray-300 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 " />
        </div>

        <div>
          <label for="password" class="block mb-2 text-sm font-medium text-gray-300e">Password</label>
          <div class="relative">
            <input :type="showPassword ? 'text' : 'password'" id="password" v-model="password" required
              class=" bg-slate-700 border border-gray-300 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-10" />
            <button type="button" @click="showPassword = !showPassword"
              class="absolute inset-y-0 right-2 flex items-center text-gray-500 hover:text-gray-900">
              <component :is="showPassword ? EyeSlashIcon : EyeIcon" class="h-5 w-5" />
            </button>
          </div>
        </div>

        <div>
          <label for="passwordConfirm" class="block mb-2 text-sm font-medium text-gray-300">Confirm Password</label>
          <div class="relative">
            <input :type="showPasswordConfirm ? 'text' : 'password'" id="passwordConfirm" v-model="passwordConfirm"
              required
              class="bg-slate-700 border border-gray-300 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-10" />
            <button type="button" @click="showPasswordConfirm = !showPasswordConfirm"
              class="absolute inset-y-0 right-2 flex items-center text-gray-500 hover:text-gray-900">
              <component :is="showPasswordConfirm ? EyeSlashIcon : EyeIcon" class="h-5 w-5" />
            </button>
          </div>
        </div>

        <button type="submit"
          class="text-white bg-blue-700 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full py-2.5 text-center ">
          Sign up
        </button>

        <h1 v-if="message" class="error py-5" v-html="message"></h1>
      </form>
      <p class="text-sm text-center font-light text-gray-300 mt-4">
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
import { useToast } from 'primevue/usetoast';
import { EyeIcon, EyeSlashIcon } from "@heroicons/vue/24/outline";

const username = ref("");
const email = ref("");
const password = ref("");
const passwordConfirm = ref("");
const message = ref("");

const showPassword = ref(false);
const showPasswordConfirm = ref(false);

const router = useRouter();
const toast = useToast(); // <-- Initialize toast

async function register() {
  if (password.value !== passwordConfirm.value) {
    message.value = "Passwords do not match.";
    toast.add({ severity: 'error', summary: 'Error', detail: 'Passwords do not match.', life: 5000 });
    return;
  }

  try {
    const response = await AuthenticationService.register({
      username: username.value,
      email: email.value,
      password: password.value,
    });

    toast.add({ severity: 'success', summary: 'Success', detail: 'Account created successfully!', life: 5000 });
    router.push({ name: "Default" });

  } catch (error: any) {
    if (error.response?.data) {
      const errData = error.response.data;
      if (errData.errors?.json) {
        const allErrorsArray = Object.values(errData.errors.json).flat();
        message.value = allErrorsArray.join("<br>");
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: "Registration failed.",
          life: 5000
        });
      } else if (errData.message) {
        message.value = `Registration failed. ${errData.message}`;
        toast.add({ severity: 'error', summary: 'Error', detail: errData.message, life: 5000 });
      } else {
        message.value = "Registration failed. Please try again.";
        toast.add({ severity: 'error', summary: 'Error', detail: 'Registration failed. Please try again.', life: 5000 });
      }
    } else {
      message.value = "Registration failed. Please try again.";
      toast.add({ severity: 'error', summary: 'Error', detail: 'Registration failed. Please try again.', life: 5000 });
    }
  }
}

</script>

<style>
.error {
  color: red;
}
</style>

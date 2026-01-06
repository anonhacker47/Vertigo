<template>
  <div class="background-container">
    <!-- Skewed image layer -->
    <div class="background-image-layer bg-cover bg-no-repeat -skew-y-6" :style="{
      backgroundImage: showDefaultWall
        ? `url(${img})`
        : `url(${bgUrl})`
    }"></div>

    <!-- Flat overlay -->
    <div class="overlay-layer"></div>

    <div class="form-wrapper absolute bg-base-100 rounded-xl shadow-[0_10px_25px_rgba(0,0,0,0.2)] p-6">
      <div class="card-body mx-4 md:mx-8 ga">
        <h1 class="text-xl text-left font-bold leading-tight tracking-tight md:text-3xl mb-4 text-white">
          Sign in to your <br /> account
        </h1>

        <form @submit.prevent="login" class="flex flex-col gap-4 z-20">
          <div class="w-full">
            <FloatLabel label="Username">
              <InputText v-model="username" placeholder="Enter username" class="w-full" />
            </FloatLabel>
          </div>

          <div>
            <FloatLabel label="Password">
              <Password v-model="password" placeholder="Enter password" :feedback="false" toggleMask class="w-full" />
            </FloatLabel>
          </div>

          <div v-if="message" class="error py-2 text-red-500 text-sm">
            {{ message }}
          </div>

          <Button label="Login" type="submit"
            class="bg-linear-to-r from-purple-500 to-indigo-500 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold shadow-lg transition-all duration-300 w-full py-3 rounded-xl" />
        </form>

        <p class="text-sm font-light text-gray-500 dark:text-gray-400 mt-4 text-center">
          Don’t have an account yet?
          <RouterLink to="/register" class="text-blue-500 underline">
            Sign up
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted } from "vue";
  import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";
import AuthenticationService from "../services/AuthenticationService";
import SeriesService from "../services/SeriesService";
import img from "../assets/logo.svg";

import InputText from "primevue/inputtext";
import Password from "primevue/password";
import FloatLabel from "primevue/floatlabel";
import Button from "primevue/button";

const userStore = useUserStore();
const router = useRouter();

const message = ref("");
const username = ref("");
const password = ref("");
const bgUrl = ref("");
const showDefaultWall = ref(false);

async function login() {
  try {
    const response = await AuthenticationService.login(
      username.value,
      password.value
    );
    userStore.addToken(response.data.access_token);

    if (localStorage.getItem("token")) {
      try {
        const userResponse = await AuthenticationService.getUser();
        userStore.addUser(userResponse.data);
      } catch (error: any) {
        message.value = error.message || "Error fetching user data";
      }
      router.push("/dashboard");
    } else {
      userStore.isUserLoggedIn = false;
    }
  } catch (error: any) {
    message.value =
      error.response?.data?.message || "An unknown error occurred.";
  }
}

const fetchBackground = async () => {
  try {
    const url = SeriesService.getSeriesThumbBg();
    // cache bust to force reload after regeneration
    bgUrl.value = `${url}?t=${Date.now()}`;
    showDefaultWall.value = false;
  } catch (e) {
    console.log(e);
  }
};

onMounted(fetchBackground);
</script>


<style scoped>
.background-container {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

/* This is the ONLY skewed element */
.background-image-layer {
  position: absolute;
  inset: -8%;
  z-index: 0;
  transform-origin: center;
}

/* Overlay stays flat */
.overlay-layer {
  position: absolute;
  inset: 0;
  backdrop-filter: blur(1px) brightness(0.7);
  background-color: rgba(27, 17, 46, 0.45);
  z-index: 10;
}

.form-wrapper {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 20;
}

.error {
  color: red;
}
</style>

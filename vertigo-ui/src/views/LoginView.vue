<template>
  <div class="background-container bg-cover bg-no-repeat"
    :style="{ backgroundImage: showDefaultWall ? 'url(' + img + ')' : '' }">
    <div class="background-images" :class="!showDefaultWall ? 'bg-base-100' : 'bg-none'">
      <div class="transform-class -skew-y-6 -translate-y-20 backdrop-blur-lg backdrop-brightness-50">
        <TransitionGroup enter-active-class="animate__animated animate__flipInX"
          leave-active-class="animate__animated animate__fadeOut">
          <div v-for="(image, index) in images" :key="index">
            <img :src="image" class="background-image" alt="comicbooks tile backdrop" />
          </div>
        </TransitionGroup>
      </div>
      <div
        class="w-fit h-fit card top-0 right-0 left-0 bottom-0 m-auto absolute z-20 w-md rounded-xl shadow-md bg-base-100 ">
        <div class="card-body mx-8 mx-4">
          <h1 class="text-xl text-center font-bold card-title leading-tight tracking-tight md:text-2xl mb-2 text-white">
            Sign in to your account
          </h1>
          <form @submit.prevent="login" class="flex gap-4 flex-col">
            <div class="form-control">
              <label for="username" class="label">
                <span class="label-text text-white">Username</span>
              </label>
              <input type="text" placeholder="Username" v-model="username" id="username"
                class="input input-bordered w-full" />
            </div>
            <div class="form-control">
              <label for="password" class="label">
                <span class="label-text text-white">Password</span>
              </label>
              <input type="password" v-model="password" id="password" class="input input-bordered w-full" />
            </div>
            <div v-if="message" class="error py-3 text-red-500">{{ message }}</div>
            <button type="submit" class="btn btn-primary mt-4 w-full">Login</button>
          </form>
          <p class="text-sm font-light text-gray-500 dark:text-gray-400 mt-4">
            Don’t have an account yet?
            <RouterLink to="/register" class="text-blue-500 underline">Sign up</RouterLink>
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useUserStore } from "../store/user";
import { useRouter } from "vue-router";
import AuthenticationService from "../services/AuthenticationService";
import SeriesService from "../services/SeriesService";
import img from "../assets/logo.svg";
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import FloatLabel from 'primevue/floatlabel'
import Button from 'primevue/button'
import Card from 'primevue/card'

const userStore = useUserStore();
const route = useRouter();
const message = ref("");
const username = ref("");
const password = ref("");
const images = ref([]);
const showDefaultWall = ref(false);

async function login() {
  try {
    const response = await AuthenticationService.login(username.value, password.value);
    userStore.addToken(response.data.access_token);

    if (localStorage.getItem("token")) {
      const headers = userStore.getTokenHeader();
      try {
        const userResponse = await AuthenticationService.getUser();
        userStore.addUser(userResponse.data);
      } catch (error) {
        message.value = error;
      }
      route.push("dashboard");
    } else {
      userStore.isUserLoggedIn = false;
    }
  } catch (error) {
    message.value = extractErrorMessage(error);
  }
}

function extractErrorMessage(error: any): string {
  if (error.response && error.response.data && error.response.data.message) {
    return error.response.data.message;
  }
  return "An unknown error occurred. Please try again.";
}

const fetchImages = async () => {
  try {
    const response = await SeriesService.getSeriesThumbBg();
    if (response.data.length > 0) {
      const seriesIds = response.data;
      const promises = seriesIds.map(async (seriesId: number) => {
        const imagesResponse = SeriesService.getImagebyId(seriesId);
        return imagesResponse;
      });
      images.value = await Promise.all(promises);
      showDefaultWall.value = false;
    } else {
      showDefaultWall.value = true;
    }
  } catch (error) {
    console.error("Error fetching images:", error);
  }
}

onMounted(() => {
  fetchImages();
});
</script>

<style scoped>
.error {
  color: red;
}

.background-container {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.background-images {
  position: relative;
  height: 100%;
  width: 100%;
}

.transform-class {
  height: 130%;
  width: 100%;
  display: grid;
  grid-auto-flow: dense;
  grid-template-columns: repeat(12, 2fr);
  grid-auto-rows: 20rem;
  margin-top: -4rem
}

.transform-class::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;

  backdrop-filter: blur(1px);
  background-color: rgba(27, 17, 46, 0.459);
  transform: scale(1);
}

.background-image {
  height: 20rem;
  width: 13.5rem;
  padding: .2rem;
}

</style>

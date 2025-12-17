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
    </div>

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
import { useUserStore } from "../store/user";
import { useRouter } from "vue-router";
import AuthenticationService from "../services/AuthenticationService";
import SeriesService from "../services/SeriesService";
import img from "../assets/logo.svg";

// PrimeVue Components
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import FloatLabel from "primevue/floatlabel";
import Button from "primevue/button";

const userStore = useUserStore();
const router = useRouter();

const message = ref("");
const username = ref("");
const password = ref("");
const images = ref([]);
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

const fetchImages = async () => {
  try {
    const response = await SeriesService.getSeriesThumbBg();
    if (response.data.length > 0) {
      const seriesIds = response.data;
      const promises = seriesIds.map(async (id: number) =>
        SeriesService.getSeriesImageById(id)
      );
      images.value = await Promise.all(promises);
      showDefaultWall.value = false;
    } else {
      showDefaultWall.value = true;
    }
  } catch (error) {
    console.error("Error fetching images:", error);
  }
};

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
  position: relative;
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
  grid-template-columns: repeat(8, 2fr);
  grid-auto-rows: 20rem;
  margin-top: -4rem;
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
  padding: 0.2rem;
}

.form-wrapper {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  /* perfectly centers it */
  z-index: 50;
  /* above overlay */
}
</style>

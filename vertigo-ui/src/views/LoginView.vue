<template>
<!-- Abstract this into a background component and also import it to signup -->
  <div class="background-container bg-cover bg-no-repeat" :style="{ backgroundImage: showDefaultWall ? 'url(' + img + ')' : ''}">
    <div class="background-images" :class="!showDefaultWall ? 'bg-base-100': 'bg-none'">
      <div class="transform-class -skew-y-6 -translate-y-20 backdrop-blur-lg backdrop-brightness-50 ">
      <div v-for="(image, index) in images" :key="index">
        <img @error="handleImageError(index)" :src="image" class="background-image" />
      </div></div>
      <PanelCardItem>
        <h1 class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
          Sign in to your account
        </h1>
        <FormKit type="form" submit-label="Login" @submit="login">
          <FormKit type="text" name="username" label="Username" validation="required" label-class="" />
          <FormKit type="password" name="password" label="Password" validation="required" />
          <h1 v-if="message != ''" class="error py-3">{{ message }}</h1>
        </FormKit>
        <p class="text-sm font-light text-gray-500 dark:text-gray-400">
          Don’t have an account yet?
          <RouterLink to="/register" class="text-blue-500 underline">Sign up</RouterLink>
        </p>
      </PanelCardItem>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import AuthenticationService from "../services/AuthenticationService";
import { useUserStore } from "../store/user";
import HeaderItem from "../components/HeaderItem.vue";
import PanelCardItem from "../components/cards/PanelCardItem.vue";
import TokenService from "../services/TokenService";
import { useRouter } from "vue-router";
import helpers from "../helpers/helpers"
import SeriesService from "../services/SeriesService";

const userStore = useUserStore();
const route = useRouter();
const message = ref("");
const auth = ref();
const images = ref([]);
const showDefaultWall = ref(false)
import img from "../assets/logo.svg";

async function login(values) {
  try {
    const response = await AuthenticationService.login(values.username, values.password);


    userStore.addToken(response.data.access_token);
    
    if (localStorage.getItem("token")) {
      const headers = TokenService.getTokenHeader();
      try {
        const response = await AuthenticationService.getUser();
        userStore.addUser(response.data.id)
      } catch (error) {
        message.value = response;
      }
      route.push("dashboard");
    } else {
      userStore.isUserLoggedIn = false;
    }
  } catch (error) {
    message.value = error;
  }
  console.log(message);
}

const fetchImages = async () => {
  try {
    const response = await SeriesService.getSeriesThumbBg();

    if (response.data .length > 0) {

    const seriesIds = response.data; // Array of all series IDs
    const promises = seriesIds.map(async (seriesId) => {
      const imagesResponse = SeriesService.getImagebyId(seriesId);      return imagesResponse;
    });
    const allImages = await Promise.all(promises);
    const newImages = helpers.ensureMinimumLength(allImages);
    images.value = newImages;
    showDefaultWall.value  = false
    } else {
      showDefaultWall.value  = true
    }

  } catch (error) {
    console.error("Error fetching images:", error);
  }

}

onMounted(() => {
  fetchImages()
});

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


.background-container {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
/* .background-container::before {
  content: "";
  position: absolute;
  background-image: url(../assets/wall.jpg);
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  filter: blur(40px);
} */

.background-images {
  position: relative;
  height: 100%;
  width: 100%;

 
  /* height of one row */
}

.transform-class{
  height: 130%;
  width: 100%;
  display: grid;
  grid-auto-flow: dense;
  grid-template-columns: repeat(8, 2fr);
  grid-auto-rows: 20rem;
  /* transform: scale(1.2); */
  /* transform: rotateY(-30deg) rotateX(40deg) perspective(800px) scale(1) */
}

.transform-class::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(7, 30, 62, 0.559);
  transform: scale(1);
  /* Adjust the opacity as needed */
}

.background-image {
  height: 20rem;
  width: 13.5rem;
  padding: .2rem;
  /* flex: 1 0 2%; */
  /* Adjust this value as per your requirement */
}
</style>

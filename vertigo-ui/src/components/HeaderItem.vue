<template>
  <nav class="bg-transparent border-b border-slate-700 flex flex-wrap items-center justify-between py-5">
    <div class="w-full flex-row container px-4 mx-auto flex flex-wrap items-center justify-between">
      <div class="relative flex justify-start">
        <RouterLink to="/"><img class="" src="../assets/logo.svg" alt="" width="40" height="40" /></RouterLink>
      </div>
      <div class="hidden justify-between items-center w-full md:flex md:w-auto navMenu" id="navbar-sticky">
        <div class="flex flex-row">
          <RouterLink to="/dashboard"
            class="block pl-2 text-white rounded mx-5 hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700">
            Dashboard</RouterLink>
          <RouterLink to="/collection"
            class="block pl-2 text-white rounded mx-5 hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700">
            Collection</RouterLink>
        </div>
      </div>

      <div class="flex md:hidden">
        <div class="dropdown dropdown-bottom dropdown-center">
          <button tabindex="0" class="btn btn-ghost btn-circle">
            <img src="../assets/menu.svg" class="h-5 w-5" alt="menu icon" />
          </button>
          <ul tabindex="0" class="dropdown-content mt-3 p-2 shadow bg-base-100 rounded-box z-50 ">
            <li>
              <RouterLink to="/dashboard"
                class="block text-white rounded  text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700">
                Dashboard
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/collection"
                class="block text-white rounded  text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700k">
                Collection
              </RouterLink>
            </li>
          </ul>
        </div>
      </div>

      <div class="flex items-center">
        <div class="flex flex-col lg:flex-row list-none">
          <div class="dropdown dropdown-hover">
            <button tabindex="0">
              <img class="inline-block h-10 w-10 rounded-md hover:opacity-75 cursor-pointer" :src="imagesrc" alt="" />
            </button>
            <ul class="dropdown-content right-0 menu z-[500] p-2 shadow bg-base-200 text-white rounded-box w-52"
              tabindex="0">
              <li>
                <RouterLink to="/settings" class="hover:text-blue-400 "> Settings</RouterLink>
              </li>
              <li>
                <a @click="logout" class="hover:text-blue-400 "> Log-out </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useUserStore } from "../store/user";
import { useRouter } from "vue-router";
import AuthenticationService from '@/services/AuthenticationService'
import { onMounted, ref, watch } from "vue";

const userStore = useUserStore();
const route = useRouter();
const imagesrc = ref('')


function logout(): void {
  userStore.logout();
  route.push("/");
}

watch(
  () => userStore.user?.profile_picture,
  async (newVal, oldVal) => {
    if (newVal && newVal !== oldVal) {
      imagesrc.value = await AuthenticationService.getUserPicture();
    }
  }
);


onMounted(async () => {
  const user = userStore.getUser();

  if (user && user.profile_picture) {
    try {
      imagesrc.value = await AuthenticationService.getUserPicture();
    } catch (error) {
      console.error("Failed to load profile picture:", error);
    }
  }
});

</script>

<style scoped>
nav {
  padding-left: 4.5rem;
  padding-right: 4.5rem;
  transition: ease-in-out;
  transition-duration: 200ms;
}

img:hover {
  transform: scale(1.1);
}

.router-link-active {
  color: #38bdf8;
}
</style>

<template>
  <nav
    class="z-50 bg-transparent border-b border-slate-700 flex flex-wrap items-center justify-between py-5"
  >
    <div
      class="w-full flex-row container px-4 mx-auto flex flex-wrap items-center justify-between"
    >
      <div class="relative flex justify-between justify-start">
        <RouterLink to="/"
          ><img class="" src="../assets/logo.svg" alt="" width="40" height="40"
        /></RouterLink>
      </div>
      <div
        class="hidden justify-between items-center w-full md:flex md:w-auto navMenu"
        id="navbar-sticky"
      >
        <div class="flex flex col">
          <RouterLink
            to="/dashboard"
            class="block pl-2 text-white rounded mx-5 hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700"
          >
            Dashboard</RouterLink
          >
          <RouterLink
            to="/collection"
            class="block pl-2 text-white rounded mx-5 hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700"
          >
            Collection</RouterLink
          >
          <!-- <RouterLink
            to="/wishlist"
            class="block pl-2 text-white rounded mx-5 hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700"
          >
            Wishlist</RouterLink
          > -->
        </div>
      </div>
      <div class="flex items-center">
        <div class="flex flex-col lg:flex-row list-none">
          <div class="dropdown dropdown-hover">
            <img
              @mouseenter="toggle"
              @mouseleave="untoggle"
              class="inline-block h-10 w-10 rounded-md hover:opacity-75 cursor-pointer"
              src="../assets/avatar.png"
              alt=""
            />

            <ul
              tabindex="0"
              class="dropdown-content right-0 menu z-50 p-2 shadow bg-base-200 text-white rounded-box w-52"
            >
              <li>
                <RouterLink to="/login" class="hover:text-blue-400 "> Settings</RouterLink>
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

<script setup>
import { useUserStore } from "../store/user";
import { useRouter } from "vue-router";
import PanelCardItem from "./cards/PanelCardItem.vue";
import { ref } from "vue";

const userStore = useUserStore();
const route = useRouter();

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("isUserLoggedIn");
  localStorage.removeItem("userId");
  userStore.isUserLoggedIn = false
  userStore.userId = null
  route.push("/");
}
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

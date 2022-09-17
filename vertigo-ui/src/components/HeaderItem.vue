<template>
  <nav
    class="relative bg-transparent border-b border-slate-700 flex flex-wrap items-center justify-between py-5"
  >
    <div
      class="w-full flex-row container px-4 mx-auto flex flex-wrap items-center justify-between"
    >
      <div class="relative flex justify-between justify-start">
        <RouterLink tag="li" to="/"
          ><img class="" src="../assets/logo.svg" alt="" width="40" height="40"
        /></RouterLink>
        <button
          class="text-white cursor-pointer text-xl leading-none px-3 border border-solid border-transparent rounded bg-transparent block lg:hidden outline-none focus:outline-none"
          type="button"
          v-on:click="toggleNavbar()"
        >
          <i class="fas fa-bars"></i>
        </button>
      </div>
      <div
        class="hidden justify-between items-center w-full md:flex md:w-auto navMenu"
        id="navbar-sticky"
      >
        <div class="flex flex col">
          <RouterLink
            tag="li"
            to="/home"
            class="block pl-2 text-white rounded mx-5 hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700"
          >
            Collection</RouterLink
          >
          <RouterLink
            tag="li"
            to="/reading"
            class="block pl-2 text-white rounded mx-5 hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700"
          >
            Reading</RouterLink
          >
          <RouterLink
            tag="li"
            to="/wishlist"
            class="block pl-2 text-white rounded mx-5 hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700"
          >
            Wishlist</RouterLink
          >
        </div>
      </div>
      <div class="flex items-center">
        <div class="flex flex-col lg:flex-row list-none">
          <div class="dropdown dropbtn">
            <img
              @mouseenter="toggle"
              @mouseleave="untoggle"
              class="inline-block h-10 w-10 rounded-md hover:opacity-75 cursor-pointer"
              src="../assets/avatar.png"
              alt=""
            />

            <div class="dropdown-content">
              <RouterLink
                tag="li"
                to="/login"
                class="nav-item px-3 flex items-center text-xs uppercase font-bold leading-snug text-white hover:opacity-75"
              >
                Settings</RouterLink
              >
              <a
                class="logout nav-item px-3 flex items-center text-xs uppercase font-bold leading-snug text-white hover:opacity-75"
                @click="logout"
              >
                Log-out
              </a>
            </div>
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

const route = useRouter();

function logout() {
  useUserStore().token = null;
  useUserStore().username = null;
  useUserStore().isUserLoggedIn = false;
  route.push("/");
}
</script>

<style scoped>
nav {
  padding-left: 4.5rem;
  padding-right: 4.5rem;
}

img {
  transition: ease-in-out;
  transition-duration: 200ms;
}

img:hover {
  transform: scale(1.1);
}

.dropbtn {
  border: none;
  cursor: pointer;
}

/* The container <div> - needed to position the dropdown content */
.dropdown {
  position: relative;
}

/* Dropdown Content (Hidden by Default) */
.dropdown-content {
  display: none;
  position: absolute;
  background-color: #0c0f15;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  right: 0 !important;
  z-index: 500;
}

/* Links inside the dropdown */
.dropdown-content a {
  color: rgb(255, 255, 255);
  padding: 16px;
  text-decoration: none;
  display: block;
}

/* Change color of dropdown links on hover */
.dropdown-content a:hover {
  background-color: #223245;
  color: aqua;
}

/* Show the dropdown menu on hover */
.dropdown:hover .dropdown-content {
  display: block;
}

.router-link-active{
  color: #38bdf8;
}


</style>

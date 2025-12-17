<template>
  <nav :class="[
    'fixed top-0 left-0 right-0 z-50 border-b border-slate-700 flex flex-wrap items-center justify-between py-3',
    props.transparentHeader
      ? 'bg-[rgba(18,25,43,0.9)] md:bg-transparent'
      : 'bg-[rgba(18,25,43,0.9)]'
  ]">
    <div class="relative flex justify-start">
      <RouterLink to="/"><img class="" src="@/assets/logo.svg" alt="" width="40" height="40" /></RouterLink>
    </div>
    <div class="hidden justify-between items-center gap-8 w-full md:flex md:w-auto navMenu" id="navbar-sticky">
      <RouterLink to="/dashboard"
        class="block text-white rounded hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700">
        Dashboard</RouterLink>
      <RouterLink to="/collection"
        class="block text-white rounded hover:bg-gray-100 text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent dark:border-gray-700">
        Collection</RouterLink>
      <li class="dropdown dropdown-hover list-none">
        <button tabindex="0"
          class="block text-white rounded  text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent">
          Browse
          <i class="pi pi-chevron-down"></i>
        </button>
        <ul class=" z-50 dropdown-content menu p-2 shadow bg-base-200 text-white text-lg rounded-box w-52" tabindex="0">
          <li>
            <RouterLink :to="{ name: 'PublisherList' }" class="hover:text-blue-400">
              Publishers
            </RouterLink>
          </li>

          <li>
            <RouterLink :to="{ name: 'CreatorList' }" class="hover:text-blue-400">
              Creators
            </RouterLink>
          </li>

          <li>
            <RouterLink :to="{ name: 'CharacterList' }" class="hover:text-blue-400">
              Characters
            </RouterLink>
          </li>
          <!-- <li>
              <RouterLink to="/genre" class="hover:text-blue-400">Genre</RouterLink>
            </li> -->
        </ul>
      </li>

    </div>



    <div class="flex md:hidden">
      <div class="dropdown dropdown-bottom dropdown-center">
        <button tabindex="0" class="btn btn-ghost btn-circle">
          <img :src="menuIcon" class="h-5 w-5" alt="menu icon" />
        </button>
        <ul tabindex="0" class="dropdown-content mt-3 shadow bg-base-100 text-center rounded-box z-50">
          <li>
            <RouterLink to="/dashboard" class="block text-white p-2 px-4 text-xl hover:bg-slate-800 rounded-box">
              Dashboard
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/collection" class="block text-white rounded-box p-2 px-4 text-xl hover:bg-slate-800">
              Collection
            </RouterLink>
          </li>
          <div class="text-white text-xl my-2 border-t-2 border-slate-700">
            <div class="text-sm text-center mt-1 text-slate-400">Browse</div>
            <div class="mt-2 flex flex-col gap-2">
              <RouterLink :to="{ name: 'PublisherList' }" class="px-4 hover:bg-slate-800 rounded-box">Publishers</RouterLink>
              <RouterLink :to="{ name: 'CreatorList' }" class="px-4 hover:bg-slate-800 rounded-box">Creators</RouterLink>
              <RouterLink :to="{ name: 'CharacterList' }" class=" px-4 hover:bg-slate-800 rounded-box">Characters</RouterLink>
            </div>
          </div>
        </ul>
      </div>
    </div>

    <div class="flex items-center">
      <div class="flex flex-col lg:flex-row list-none">
        <div class="dropdown dropdown-hover">
          <button tabindex="0">
            <img class="inline-block h-9 w-9 rounded-md hover:opacity-75 cursor-pointer" @error="changeThumb()"
              :src="imagesrc" alt="" />
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
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import AuthenticationService from '@/services/AuthenticationService'
import menuIcon from '@/assets/menu.svg'

const props = defineProps<{
  transparentHeader?: boolean
}>()

const router = useRouter()
const userStore = useUserStore()

const imagesrc = ref('')
const mobileOpen = ref(false)
const profileMenu = ref()

const dummy = new URL('@/assets/user.svg', import.meta.url).href

function changeThumb() {
  imagesrc.value = dummy
}

function logout() {
  userStore.logout()
  router.push('/')
}

/* Unified menu structure */
const menuItems = [
  {
    label: 'Dashboard',
    command: () => router.push('/dashboard')
  },
  {
    label: 'Collection',
    command: () => router.push('/collection')
  },
  {
    label: 'Browse',
    items: [
      { label: 'Publishers', command: () => router.push({ name: 'PublisherList' }) },
      { label: 'Creators', command: () => router.push({ name: 'CreatorList' }) },
      { label: 'Characters', command: () => router.push({ name: 'CharacterList' }) }
    ]
  }
]

const profileItems = [
  {
    label: 'Settings',
    icon: 'pi pi-cog',
    command: () => router.push('/settings')
  },
  {
    label: 'Log out',
    icon: 'pi pi-sign-out',
    command: logout
  }
]

watch(
  () => userStore.user?.profile_picture,
  async (val) => {
    if (val) imagesrc.value = await AuthenticationService.getUserPicture()
  }
)

onMounted(async () => {
  try {
    const user = userStore.getUser()

    if (user?.profile_picture) {
      imagesrc.value = await AuthenticationService.getUserPicture()
    } else {
      imagesrc.value = dummy
    }
  } catch (error) {
    console.error("Failed to load user profile picture:", error)
    imagesrc.value = dummy
  }
})
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

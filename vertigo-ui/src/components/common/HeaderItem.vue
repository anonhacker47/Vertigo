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
      <div class="dropdown dropdown-hover list-none">
        <button tabindex="0"
          class="block text-white rounded  text-xl md:hover:bg-transparent md:hover:text-sky-300 md:p-0 hover:text-blue bg-transparent">
          Browse
          <i class="pi pi-chevron-down"></i>
        </button>
        <ul class="z-50 dropdown-content menu p-2 shadow bg-base-200 text-white text-lg rounded-box w-52" tabindex="0">
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
        </ul>
      </div>

    </div>


    <div class="flex md:hidden">
      <Button icon="pi pi-bars" class="p-button-text p-button-rounded p-button-lg text-white"
        @click="mobileOpen = true" />
    </div>

    <Drawer v-model:visible="mobileOpen" position="right" class="w-72 flex justify-between bg-[#12192b]">
      <div class="flex items-center w-full justify-center gap-3 mb-6">
        <img class="inline-block h-30 w-30 rounded-md" @error="changeThumb()" :src="imagesrc" alt="" />
      </div>

      <PanelMenu :model="menuItems" class="border-none" />

      <div class="mt-8">
        <button class="w-full text-left text-white py-2 hover:text-sky-300" @click="router.push('/settings')">
          <i class="pi pi-cog mr-2"></i> Settings
        </button>

        <button class="w-full text-left text-white py-2 hover:text-red-400" @click="logout">
          <i class="pi pi-sign-out mr-2"></i> Log out
        </button>
      </div>
    </Drawer>

    <div class="hidden md:flex items-center">
      <div class="flex flex-col lg:flex-row list-none">
        <div class="dropdown dropdown-hover">
          <button tabindex="0">
            <img class="inline-block h-9 w-9 rounded-md hover:opacity-75 cursor-pointer" @error="changeThumb()"
              :src="imagesrc" alt="" />
          </button>
          <ul class="dropdown-content right-0 menu z-[500] p-2 shadow bg-base-200 text-white rounded-box w-52"
            tabindex="-1">
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

const menuItems = [
  {
    label: 'Dashboard',
    icon: 'pi pi-home',
    command: () => {
      mobileOpen.value = false
      router.push('/dashboard')
    }
  },
  {
    label: 'Collection',
    icon: 'pi pi-book',
    command: () => {
      mobileOpen.value = false
      router.push('/collection')
    }
  },
  {
    label: 'Browse',
    icon: '',
    items: [
      {
        label: 'Publishers',
        icon: 'pi pi-print',
        command: () => router.push({ name: 'PublisherList' })
      },
      {
        label: 'Creators',
        icon: 'pi pi-user',
        command: () => router.push({ name: 'CreatorList' })
      },
      {
        label: 'Characters',
        icon: 'pi pi-users',
        command: () => router.push({ name: 'CharacterList' })
      }
    ]
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

.router-link-active {
  color: #38bdf8;
}

:deep(.p-panelmenu-header-content) {
  background: transparent;
  color: white;
}

:deep(.p-panelmenu-content) {
  background: transparent;
}

:deep(.p-menuitem-link) {
  color: white;
}

:deep(.p-menuitem-link:hover) {
  color: #38bdf8;
}
</style>

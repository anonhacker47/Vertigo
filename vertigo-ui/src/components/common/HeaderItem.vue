<template>
  <nav :class="[
    'fixed top-0 left-0 right-0 z-50 h-header border-b border-slate-700 px-6 md:px-16 transition-all duration-200 flex items-center',
    props.transparentHeader && !scrolled
      ? 'bg-[rgba(18,25,43,0.9)] md:bg-transparent'
      : 'bg-[rgba(18,25,43,0.9)]'
  ]">
    
    <!-- Desktop: equal side columns keep the link group dead centre whatever sits beside it. -->
    <div class="hidden w-full grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center md:grid">
      <RouterLink to="/" class="justify-self-start">
        <img src="@/assets/logo.svg" alt="Logo" width="40" height="40" />
      </RouterLink>

      <div class="flex items-center gap-8">
        <RouterLink to="/dashboard" class="text-white text-lg hover:text-sky-300 transition-colors">
          Dashboard
        </RouterLink>
        <RouterLink to="/collection" class="text-white text-lg hover:text-sky-300 transition-colors">
          Collection
        </RouterLink>
        <RouterLink to="/insights" class="text-white text-lg hover:text-sky-300 transition-colors">
          Insights
        </RouterLink>

        <div class="dropdown dropdown-hover list-none">
          <button tabindex="0" class="text-white text-lg hover:text-sky-300 transition-colors flex items-center gap-1">
            Browse
            <i class="pi pi-chevron-down text-sm"></i>
          </button>
          <div class="dropdown-content z-50 pt-2">
            <ul class="menu p-2 shadow bg-base-200 text-white text-md rounded-box w-52" tabindex="0">
              <li><RouterLink :to="{ name: 'PublisherList' }" class="hover:text-blue-400">Publishers</RouterLink></li>
              <li><RouterLink :to="{ name: 'CreatorList' }" class="hover:text-blue-400">Creators</RouterLink></li>
              <li><RouterLink :to="{ name: 'CharacterList' }" class="hover:text-blue-400">Characters</RouterLink></li>
              <li class="my-1 border-t border-slate-600" aria-hidden="true"></li>
              <li><RouterLink :to="{ name: 'TierList' }" class="hover:text-blue-400">Tier List</RouterLink></li>
            </ul>
          </div>
        </div>
      </div>

      <div class="flex min-w-0 items-center justify-end gap-5">
        <GlobalSearch class="hidden lg:block" @summon="summonSearch" />
        <!-- Tablet widths have no room for the box, so an icon opens it over the links. -->
        <button type="button" class="hidden h-9 w-9 place-items-center rounded-lg text-slate-300 transition hover:bg-slate-800 hover:text-white md:grid lg:hidden"
          aria-label="Search" title="Search (/)" @click="searchOpen = true">
          <i class="pi pi-search"></i>
        </button>

        <div class="dropdown dropdown-hover">
          <button tabindex="0" class="flex items-center">
            <img class="inline-block h-9 w-9 rounded-md hover:opacity-75 cursor-pointer object-cover" @error="changeThumb()" :src="imagesrc" alt="Profile" />
          </button>
          <div class="dropdown-content right-0 z-500 pt-2">
            <ul class="menu p-2 shadow bg-base-200 text-white rounded-box w-52" tabindex="-1">
              <li><RouterLink to="/settings" class="hover:text-blue-400">Settings</RouterLink></li>
              <li><a @click="logout" class="hover:text-blue-400">Log-out</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div v-if="searchOpen" class="absolute inset-y-0 left-[4.5rem] right-[4.5rem] z-20 hidden items-center gap-3 bg-[rgba(18,25,43,0.98)] md:flex lg:hidden">
      <GlobalSearch wide autofocus class="flex-1" @navigate="searchOpen = false" @dismiss="searchOpen = false" />
      <button type="button" class="grid h-9 w-9 place-items-center rounded-lg text-slate-300 transition hover:bg-slate-800 hover:text-white"
        aria-label="Close search" @click="searchOpen = false">
        <i class="pi pi-times"></i>
      </button>
    </div>

    <div class="flex md:hidden justify-between items-center w-full">
      <RouterLink to="/">
        <img src="@/assets/logo.svg" alt="Logo" width="40" height="40" />
      </RouterLink>
      <Button icon="pi pi-bars" class="p-button-text p-button-rounded p-button-lg text-white" @click="mobileOpen = true" />
    </div>

    <Drawer v-model:visible="mobileOpen" position="right" class="w-72 flex justify-between bg-[#12192b]">
      <div class="flex items-center w-full justify-center gap-3 mb-6">
        <img class="inline-block h-30 w-30 rounded-md" @error="changeThumb()" :src="imagesrc" alt="" />
      </div>

      <GlobalSearch block class="mb-5" @navigate="mobileOpen = false" />

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

  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import AuthenticationService from '@/services/AuthenticationService'
import GlobalSearch from '@/components/common/GlobalSearch.vue'
import menuIcon from '@/assets/menu.svg'

const props = defineProps<{
  transparentHeader?: boolean
}>()

const router = useRouter()
const userStore = useUserStore()

const imagesrc = ref('')
const mobileOpen = ref(false)
const searchOpen = ref(false)
function summonSearch() {
  if (window.innerWidth >= 768) searchOpen.value = true
}
const profileMenu = ref()

const scrolled = ref(false)
function onScroll() {
  scrolled.value = window.scrollY > 16
}
onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))

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
    label: 'Insights',
    icon: 'pi pi-chart-bar',
    command: () => {
      mobileOpen.value = false
      router.push('/insights')
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
      },
      { separator: true },
      {
        label: 'Tier List',
        icon: 'pi pi-sort-amount-down',
        command: () => router.push({ name: 'TierList' })
      }
    ]
  }
]


watch(
  () => userStore.user,
  async (user) => {
    try {
      imagesrc.value = user?.profile_picture ? await AuthenticationService.getUserPicture() : dummy
    } catch (error) {
      console.error("Failed to load user profile picture:", error)
      imagesrc.value = dummy
    }
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

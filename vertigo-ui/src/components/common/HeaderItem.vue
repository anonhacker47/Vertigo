<template>
  <nav :class="[
    'fixed top-0 left-0 right-0 z-50 h-header border-b border-slate-700 backdrop-blur-md transition-all duration-200 flex items-center',
    props.transparentHeader && !scrolled
      ? 'bg-[rgba(18,25,43,0.9)] md:bg-transparent'
      : 'bg-[rgba(18,25,43,0.9)]'
  ]">
    
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
        <JobsIndicator />
        <!-- Tablets: no room for the box, so an icon opens it as an overlay. -->
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

    <div v-if="searchOpen" class="absolute inset-y-0 left-5 right-5 z-20 flex items-center gap-3 bg-[rgba(18,25,43,0.98)] md:left-[4.5rem] md:right-[4.5rem] lg:hidden">
      <GlobalSearch wide autofocus class="flex-1" @navigate="searchOpen = false" @dismiss="searchOpen = false" />
      <button type="button" class="grid h-9 w-9 place-items-center rounded-lg text-slate-300 transition hover:bg-slate-800 hover:text-white"
        aria-label="Close search" @click="searchOpen = false">
        <i class="pi pi-times"></i>
      </button>
    </div>

    <div class="flex w-full items-center justify-between md:hidden">
      <RouterLink to="/" aria-label="Home">
        <img src="@/assets/logo.svg" alt="" width="36" height="36" />
      </RouterLink>
      <div class="flex items-center gap-1">
        <button type="button" class="nav-icon" aria-label="Search" @click="searchOpen = true">
          <i class="pi pi-search"></i>
        </button>
        <JobsIndicator />
        <button type="button" class="nav-icon" aria-label="Open menu" @click="mobileOpen = true">
          <i class="pi pi-bars"></i>
        </button>
      </div>
    </div>

    <Drawer v-model:visible="mobileOpen" position="right" class="mnav" style="width: min(88vw, 22rem)" :show-close-icon="false">
      <template #header>
        <div class="mnav__who">
          <img class="mnav__avatar" :src="imagesrc" alt="" @error="changeThumb()" />
          <div class="min-w-0 flex-1">
            <p class="mnav__name">{{ userName }}</p>
            <p v-if="userEmail" class="mnav__email">{{ userEmail }}</p>
          </div>
          <button type="button" class="nav-icon" aria-label="Close menu" @click="mobileOpen = false">
            <i class="pi pi-times"></i>
          </button>
        </div>
      </template>

      <nav class="mnav__list" aria-label="Main">
        <RouterLink v-for="link in mainLinks" :key="link.label" :to="link.to" class="mnav__row" @click="mobileOpen = false">
          <i :class="link.icon" aria-hidden="true"></i>
          <span>{{ link.label }}</span>
        </RouterLink>
      </nav>

      <div>
        <p class="mnav__section">Browse</p>
        <nav class="mnav__list" aria-label="Browse">
          <RouterLink v-for="link in browseLinks" :key="link.label" :to="link.to" class="mnav__row" @click="mobileOpen = false">
            <i :class="link.icon" aria-hidden="true"></i>
            <span>{{ link.label }}</span>
          </RouterLink>
        </nav>
      </div>

      <template #footer>
        <nav class="mnav__list" aria-label="Account">
          <RouterLink to="/settings" class="mnav__row" @click="mobileOpen = false">
            <i class="pi pi-cog" aria-hidden="true"></i>
            <span>Settings</span>
          </RouterLink>
          <button type="button" class="mnav__row mnav__row--leave" @click="logout">
            <i class="pi pi-sign-out" aria-hidden="true"></i>
            <span>Log out</span>
          </button>
        </nav>
      </template>
    </Drawer>

  </nav>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import AuthenticationService from '@/services/AuthenticationService'
import GlobalSearch from '@/components/common/GlobalSearch.vue'
import JobsIndicator from '@/components/common/JobsIndicator.vue'

const props = defineProps<{
  transparentHeader?: boolean
}>()

const router = useRouter()
const userStore = useUserStore()

const imagesrc = ref('')
const mobileOpen = ref(false)
// Overlay search below the large breakpoint; "/" summons it when the inline box is hidden.
const searchOpen = ref(false)
function summonSearch() {
  searchOpen.value = true
}

const userName = computed(() => userStore.user?.username ?? 'Your shelf')
const userEmail = computed(() => userStore.user?.email ?? '')

const mainLinks = [
  { label: 'Dashboard', icon: 'pi pi-home', to: '/dashboard' },
  { label: 'Collection', icon: 'pi pi-book', to: '/collection' },
  { label: 'Insights', icon: 'pi pi-chart-bar', to: '/insights' },
]
const browseLinks = [
  { label: 'Publishers', icon: 'pi pi-print', to: { name: 'PublisherList' } },
  { label: 'Creators', icon: 'pi pi-user', to: { name: 'CreatorList' } },
  { label: 'Characters', icon: 'pi pi-users', to: { name: 'CharacterList' } },
  { label: 'Tier list', icon: 'pi pi-sort-amount-down', to: { name: 'TierList' } },
]

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
  mobileOpen.value = false
  userStore.logout()
  router.push('/')
}

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
  padding-left: 1.25rem;
  padding-right: 1.25rem;
}
@media (min-width: 768px) {
  nav {
    padding-left: 4.5rem;
    padding-right: 4.5rem;
  }
}

.router-link-active {
  color: #38bdf8;
}

.nav-icon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  flex: none;
  border-radius: 999px;
  color: #e2e8f0;
  font-size: 17px;
  transition: background-color 0.12s ease;
}
.nav-icon:hover {
  background: rgba(255, 255, 255, 0.08);
}
.nav-icon:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}

.mnav {
  background: #0f172a;
  color: #e2e8f0;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
}
:deep(.p-drawer-header) {
  padding: 16px 12px 8px 16px;
}
:deep(.p-drawer-content) {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 10px 12px 16px;
}
:deep(.p-drawer-footer) {
  padding: 10px 12px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.mnav__who {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 12px;
}
.mnav__avatar {
  width: 46px;
  height: 46px;
  flex: none;
  border-radius: 12px;
  object-fit: cover;
  background: #1e293b;
}
.mnav__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #fff;
  font-size: 16px;
  font-weight: 800;
  line-height: 1.2;
}
.mnav__email {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #94a3b8;
  font-size: 12.5px;
  font-weight: 600;
}

.mnav__section {
  padding: 0 14px 6px;
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
}
.mnav__list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.mnav__row {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 14px;
  min-height: 48px;
  padding: 0 14px;
  border-radius: 12px;
  color: #e2e8f0;
  font-size: 16px;
  font-weight: 700;
  text-align: left;
  transition: background-color 0.12s ease, color 0.12s ease;
}
.mnav__row i {
  width: 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 16px;
}
.mnav__row:hover {
  background: rgba(255, 255, 255, 0.06);
}
.mnav__row:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: -2px;
}
.mnav__row.router-link-active {
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
}
.mnav__row.router-link-active i {
  color: #38bdf8;
}
.mnav__row--leave:hover,
.mnav__row--leave:hover i {
  color: #fda4af;
}

@media (prefers-reduced-motion: reduce) {
  .nav-icon,
  .mnav__row {
    transition: none;
  }
}
</style>

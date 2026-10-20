<template>
  <div class="mx-auto w-full max-w-page px-6 py-8 md:px-10 md:py-10">
    <div class="mx-auto flex w-full max-w-6xl flex-col gap-8">

      <header class="flex items-center gap-5">
        <img :src="avatar" @error="onAvatarError" alt=""
          class="h-16 w-16 shrink-0 rounded-xl border border-slate-700 bg-slate-900 object-cover" />
        <div class="min-w-0">
          <h1 class="truncate text-2xl font-bold leading-tight text-slate-100">
            {{ user?.username || 'Your account' }}
          </h1>
          <p class="mt-1 flex flex-wrap gap-x-4 text-sm text-slate-400">
            <span class="truncate">{{ user?.email }}</span>
            <span v-if="memberSince">Collecting since {{ memberSince }}</span>
          </p>
        </div>
      </header>

      <div class="grid gap-6 border-t border-slate-800/60 pt-8 lg:grid-cols-[15rem_minmax(0,1fr)] lg:gap-12">
        <nav aria-label="Settings sections" class="-mx-6 px-6 lg:mx-0 lg:px-0">
          <ul class="flex gap-1 overflow-x-auto pb-1 lg:sticky lg:top-[calc(var(--spacing-header)+2rem)] lg:flex-col lg:overflow-visible lg:pb-0">
            <li v-for="section in sections" :key="section.name">
              <RouterLink :to="{ name: section.name }" class="nav-link" active-class="is-active">
                <i :class="section.icon" aria-hidden="true"></i>
                <span class="min-w-0">
                  <span class="block">{{ section.label }}</span>
                  <span class="hint hidden lg:block">{{ section.hint }}</span>
                </span>
              </RouterLink>
            </li>
          </ul>
        </nav>

        <main class="min-w-0">
          <RouterView />
        </main>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useUserStore } from "@/store/user";
import type { User } from "@/types/user.types";
import AuthenticationService from "@/services/AuthenticationService";
import fallbackAvatar from "@/assets/user.svg";

const sections = [
  { name: "SettingsProfile", label: "Profile", hint: "Photo, name, email and currency", icon: "pi pi-user" },
  { name: "SettingsSecurity", label: "Security", hint: "Password", icon: "pi pi-lock" },
  { name: "SettingsIntegrations", label: "Integrations", hint: "Metron and MyAnimeList", icon: "pi pi-link" },
  { name: "SettingsData", label: "Your data", hint: "Export or delete everything", icon: "pi pi-database" },
];

const userStore = useUserStore();

const user = computed<User | null>(() => userStore.user ?? userStore.getUser());

const memberSince = computed(() => {
  const seen = user.value?.first_seen;
  if (!seen) return "";
  const d = new Date(seen);
  return Number.isNaN(d.getTime())
    ? ""
    : d.toLocaleDateString(undefined, { month: "long", year: "numeric" });
});

const avatar = ref<string>(fallbackAvatar);
const avatarUrl = ref("");
const loadedPicture = ref<string | null | undefined>(undefined);

function releaseAvatar() {
  if (avatarUrl.value) URL.revokeObjectURL(avatarUrl.value);
  avatarUrl.value = "";
}

async function loadAvatar(current: User | null) {
  releaseAvatar();
  loadedPicture.value = current?.profile_picture;
  if (current?.profile_picture) {
    try {
      avatarUrl.value = await AuthenticationService.getUserPicture();
    } catch (e) {
      console.error("Failed to load profile picture:", e);
    }
  }
  avatar.value = avatarUrl.value || fallbackAvatar;
}

function onAvatarError() {
  avatar.value = fallbackAvatar;
}

watch(
  () => userStore.user,
  async (fresh) => {
    if (fresh && fresh.profile_picture !== loadedPicture.value) await loadAvatar(fresh);
  }
);

onMounted(async () => {
  const cached = userStore.getUser();
  if (cached && !userStore.user) userStore.addUser(cached);
  else await loadAvatar(user.value);

  try {
    const response = await AuthenticationService.getUser();
    userStore.addUser(response.data);
  } catch (e) {
    console.error("Failed to refresh account details:", e);
  }
});

onUnmounted(releaseAvatar);
</script>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border-radius: 10px;
  color: #94a3b8;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.25;
  white-space: nowrap;
  transition: color 0.12s ease, background-color 0.12s ease;
}
.nav-link i {
  font-size: 15px;
  flex: none;
}
.nav-link:hover {
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.03);
}
.nav-link.is-active {
  color: #fff;
  background: #1e293b;
}
.nav-link:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}
.nav-link .hint {
  margin-top: 2px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  white-space: normal;
}
.nav-link.is-active .hint {
  color: #94a3b8;
}
</style>

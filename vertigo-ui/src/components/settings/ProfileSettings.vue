<template>
  <SettingsSection>
    <SettingsPanel as="form" title="Photo and name" @submit.prevent="saveProfile">
      <div class="flex flex-col gap-6">
        <div class="flex flex-col gap-2">
          <span class="text-sm font-medium text-slate-300">Photo</span>
          <div class="flex flex-wrap items-start gap-5">
            <img :src="avatarPreview" @error="onAvatarError" alt=""
              class="h-20 w-20 shrink-0 rounded-xl border border-slate-700 bg-slate-900 object-cover" />
            <div class="flex min-w-0 flex-1 flex-col gap-2">
              <div class="flex flex-wrap items-center gap-2">
                <Button type="button" label="Upload photo" icon="pi pi-upload" size="small" outlined
                  @click="fileInput?.click()" />
                <Button v-if="hasPhoto" type="button" label="Remove" size="small" text severity="secondary"
                  @click="removePhoto" />
              </div>
              <button type="button"
                class="w-fit text-xs text-slate-400 underline-offset-2 transition hover:text-slate-200 hover:underline"
                @click="showLinkInput = !showLinkInput">
                {{ showLinkInput ? 'Hide the link field' : 'Use an image link instead' }}
              </button>
              <InputText v-if="showLinkInput" v-model.trim="photoLink" size="small" class="w-full sm:w-80"
                placeholder="https://example.com/photo.jpg" @change="usePhotoLink" @keydown.enter.prevent="usePhotoLink" />
              <p class="text-xs text-slate-500">Shown in the top bar. JPG, PNG or WebP.</p>
            </div>
          </div>
          <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFileChosen" />
        </div>

        <div class="grid gap-5 sm:grid-cols-2">
          <div class="flex flex-col gap-1.5">
            <label for="username" class="text-sm font-medium text-slate-300">Username</label>
            <InputText id="username" v-model.trim="form.username" autocomplete="username" class="w-full"
              :invalid="!!fieldError('username')" />
            <p v-if="fieldError('username')" class="text-xs text-red-400">{{ fieldError('username') }}</p>
          </div>
          <div class="flex flex-col gap-1.5">
            <label for="email" class="text-sm font-medium text-slate-300">Email</label>
            <InputText id="email" v-model.trim="form.email" type="email" autocomplete="email" class="w-full"
              :invalid="!!fieldError('email')" />
            <p v-if="fieldError('email')" class="text-xs text-red-400">{{ fieldError('email') }}</p>
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <label for="currency" class="text-sm font-medium text-slate-300">Currency</label>
          <Select inputId="currency" v-model="form.currency" :options="currencyOptions" optionLabel="name"
            optionValue="code" filter :filterFields="['code', 'name']" filterPlaceholder="Search by code or name"
            placeholder="Choose a currency" class="w-full sm:w-80">
            <template #value="{ value, placeholder }">
              <span v-if="value" class="flex items-baseline gap-2">
                <span class="font-semibold tabular-nums">{{ value }}</span>
                <span class="truncate text-slate-400">{{ currencyName(value) }}</span>
              </span>
              <span v-else>{{ placeholder }}</span>
            </template>
            <template #option="{ option }">
              <span class="flex items-baseline gap-2">
                <span class="w-10 font-semibold tabular-nums">{{ option.code }}</span>
                <span class="truncate text-slate-400">{{ option.name }}</span>
              </span>
            </template>
          </Select>
          <p class="text-xs text-slate-500">Used for purchase prices across the app and in the export.</p>
        </div>
      </div>

      <template #footer>
        <Button v-if="profileDirty" type="button" label="Reset" size="small" text severity="secondary"
          :disabled="savingProfile" @click="resetProfile" />
        <Button type="submit" label="Save changes" size="small" :loading="savingProfile"
          :disabled="!profileDirty || hasProfileErrors" />
      </template>
    </SettingsPanel>
  </SettingsSection>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from "vue";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import { useUserStore } from "@/store/user";
import type { User } from "@/types/user.types";
import AuthenticationService from "@/services/AuthenticationService";
import { currencyOptions, currencyName } from "@/utils/currencies";
import fallbackAvatar from "@/assets/user.svg";
import SettingsSection from "@/components/settings/SettingsSection.vue";
import SettingsPanel from "@/components/settings/SettingsPanel.vue";

const toast = useToast();
const userStore = useUserStore();

type ProfileFields = { username: string; email: string; currency: string };

const original = reactive<ProfileFields>({ username: "", email: "", currency: "" });
const form = reactive<ProfileFields>({ username: "", email: "", currency: "" });

const storedAvatar = ref("");
const loadedPicture = ref<string | null | undefined>(undefined);
const avatarPreview = ref<string>(fallbackAvatar);
const pendingPhoto = ref<File | string | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);
const showLinkInput = ref(false);
const photoLink = ref("");
const savingProfile = ref(false);

const hasPhoto = computed(
  () => pendingPhoto.value !== "noimage" && (pendingPhoto.value !== null || !!storedAvatar.value)
);

const profileDirty = computed(
  () =>
    pendingPhoto.value !== null ||
    form.username !== original.username ||
    form.email !== original.email ||
    form.currency !== original.currency
);

const profileErrors = computed(() => {
  const e: Partial<Record<keyof ProfileFields, string>> = {};
  if (!form.username) e.username = "Enter a username.";
  else if (form.username.length < 3) e.username = "Use at least 3 characters.";
  else if (!/^[A-Za-z]/.test(form.username)) e.username = "Start with a letter.";
  if (!form.email) e.email = "Enter an email address.";
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = "Enter a valid email address.";
  return e;
});
const hasProfileErrors = computed(() => Object.keys(profileErrors.value).length > 0);

function fieldError(field: keyof ProfileFields) {
  return form[field] !== original[field] ? profileErrors.value[field] : undefined;
}

function currentUser(): User | null {
  return userStore.user ?? userStore.getUser();
}

function applyUser(user: User | null) {
  original.username = user?.username || "";
  original.email = user?.email || "";
  original.currency = user?.preferred_currency || "USD";
  Object.assign(form, original);
}

function releaseStoredAvatar() {
  if (storedAvatar.value) URL.revokeObjectURL(storedAvatar.value);
  storedAvatar.value = "";
}

async function loadStoredAvatar(user: User | null) {
  releaseStoredAvatar();
  loadedPicture.value = user?.profile_picture;
  if (user?.profile_picture) {
    try {
      storedAvatar.value = await AuthenticationService.getUserPicture();
    } catch (e) {
      console.error("Failed to load profile picture:", e);
    }
  }
  if (pendingPhoto.value === null) avatarPreview.value = storedAvatar.value || fallbackAvatar;
}

function onFileChosen(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  pendingPhoto.value = file;
  avatarPreview.value = URL.createObjectURL(file);
  input.value = "";
}

function usePhotoLink() {
  if (!photoLink.value) return;
  pendingPhoto.value = photoLink.value;
  avatarPreview.value = photoLink.value;
}

function removePhoto() {
  pendingPhoto.value = "noimage";
  avatarPreview.value = fallbackAvatar;
  photoLink.value = "";
}

function onAvatarError() {
  avatarPreview.value = fallbackAvatar;
}

function resetProfile() {
  Object.assign(form, original);
  pendingPhoto.value = null;
  photoLink.value = "";
  showLinkInput.value = false;
  avatarPreview.value = storedAvatar.value || fallbackAvatar;
}

async function saveProfile() {
  if (!profileDirty.value || hasProfileErrors.value) return;

  const data = new FormData();
  if (form.username !== original.username) data.append("username", form.username);
  if (form.email !== original.email) data.append("email", form.email);
  if (form.currency !== original.currency) data.append("preferred_currency", form.currency);
  if (pendingPhoto.value !== null) data.append("profile_picture", pendingPhoto.value);
  const photoChanged = pendingPhoto.value !== null;

  savingProfile.value = true;
  try {
    const response = await AuthenticationService.updateUser(data);
    applyUser(response.data);
    pendingPhoto.value = null;
    photoLink.value = "";
    showLinkInput.value = false;
    if (photoChanged) await loadStoredAvatar(response.data);
    userStore.addUser(response.data);
    toast.add({ severity: "success", summary: "Saved", detail: "Your profile is up to date.", life: 3000 });
  } catch (error: any) {
    toast.add({ severity: "error", summary: "Couldn't save", detail: error.message, life: 5000 });
  } finally {
    savingProfile.value = false;
  }
}

// Pick up the layout's account refresh unless the user is mid-edit.
watch(
  () => userStore.user,
  async (fresh) => {
    if (!fresh) return;
    if (!profileDirty.value) applyUser(fresh);
    if (fresh.profile_picture !== loadedPicture.value) await loadStoredAvatar(fresh);
  }
);

onMounted(async () => {
  const user = currentUser();
  applyUser(user);
  await loadStoredAvatar(user);
});

onUnmounted(releaseStoredAvatar);
</script>

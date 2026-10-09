<template>
  <div class="mx-auto w-full max-w-page px-6 py-8 md:px-10 md:py-10">
    <div class="mx-auto flex w-full max-w-5xl flex-col gap-10">

      <header class="flex items-center gap-5">
        <img :src="avatarPreview" @error="onAvatarError" alt=""
          class="h-16 w-16 shrink-0 rounded-xl border border-slate-700 bg-slate-900 object-cover" />
        <div class="min-w-0">
          <h1 class="truncate text-2xl font-bold leading-tight text-slate-100">
            {{ original.username || 'Your account' }}
          </h1>
          <p class="mt-1 flex flex-wrap gap-x-4 text-sm text-slate-400">
            <span class="truncate">{{ original.email }}</span>
            <span v-if="memberSince">Collecting since {{ memberSince }}</span>
          </p>
        </div>
      </header>

      <section class="grid gap-5 border-t border-slate-800/60 pt-8 lg:grid-cols-[15rem_minmax(0,1fr)] lg:gap-10">
        <div>
          <h2 class="text-lg font-semibold text-slate-100">Profile</h2>
          <p class="mt-1 text-sm leading-relaxed text-slate-400">
            Your name and photo, and the currency purchase prices are shown in.
          </p>
        </div>

        <form class="rounded-xl border border-slate-800/60 bg-slate-900/40" @submit.prevent="saveProfile">
          <div class="flex flex-col gap-6 p-6">

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

          <div class="flex items-center justify-end gap-2 border-t border-slate-800/60 px-6 py-4">
            <Button v-if="profileDirty" type="button" label="Reset" size="small" text severity="secondary"
              :disabled="savingProfile" @click="resetProfile" />
            <Button type="submit" label="Save changes" size="small" :loading="savingProfile"
              :disabled="!profileDirty || hasProfileErrors" />
          </div>
        </form>
      </section>

      <section class="grid gap-5 border-t border-slate-800/60 pt-8 lg:grid-cols-[15rem_minmax(0,1fr)] lg:gap-10">
        <div>
          <h2 class="text-lg font-semibold text-slate-100">Password</h2>
          <p class="mt-1 text-sm leading-relaxed text-slate-400">
            You'll stay signed in on this device after changing it.
          </p>
        </div>

        <form class="rounded-xl border border-slate-800/60 bg-slate-900/40" @submit.prevent="changePassword"
          autocomplete="off">
          <div class="flex flex-col gap-5 p-6 sm:max-w-sm">
            <div class="flex flex-col gap-1.5">
              <label for="current-password" class="text-sm font-medium text-slate-300">Current password</label>
              <Password inputId="current-password" v-model="pw.current" :feedback="false" toggleMask fluid
                autocomplete="current-password" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label for="new-password" class="text-sm font-medium text-slate-300">New password</label>
              <Password inputId="new-password" v-model="pw.next" :feedback="false" toggleMask fluid
                autocomplete="new-password" :invalid="pwTooShort" />
              <p v-if="pwTooShort" class="text-xs text-red-400">Use at least 3 characters.</p>
            </div>
            <div class="flex flex-col gap-1.5">
              <label for="confirm-password" class="text-sm font-medium text-slate-300">Confirm new password</label>
              <Password inputId="confirm-password" v-model="pw.confirm" :feedback="false" toggleMask fluid
                autocomplete="new-password" :invalid="pwMismatch" />
              <p v-if="pwMismatch" class="text-xs text-red-400">These passwords don't match.</p>
            </div>
          </div>
          <div class="flex items-center justify-end border-t border-slate-800/60 px-6 py-4">
            <Button type="submit" label="Change password" size="small" :loading="changingPassword"
              :disabled="!canChangePassword" />
          </div>
        </form>
      </section>

      <section class="grid gap-5 border-t border-slate-800/60 pt-8 lg:grid-cols-[15rem_minmax(0,1fr)] lg:gap-10">
        <div>
          <h2 class="text-lg font-semibold text-slate-100">Your data</h2>
          <p class="mt-1 text-sm leading-relaxed text-slate-400">
            Everything you've catalogued: series, issues, publishers, creators, characters and genres.
          </p>
        </div>

        <div class="flex flex-col gap-5">
          <div
            class="flex flex-col gap-4 rounded-xl border border-slate-800/60 bg-slate-900/40 p-6 sm:flex-row sm:items-start sm:justify-between">
            <div class="min-w-0">
              <h3 class="font-semibold text-slate-100">Export as a spreadsheet</h3>
              <p class="mt-1 max-w-prose text-sm leading-relaxed text-slate-400">
                An .xlsx file with a Series sheet, an Issues sheet and a Stats sheet.
                Prices are in {{ currencyName(original.currency) || original.currency }}.
              </p>
            </div>
            <Button type="button" label="Download .xlsx" icon="pi pi-download" size="small" outlined
              class="shrink-0" :loading="exporting" @click="exportCollection" />
          </div>

          <div class="rounded-xl border border-red-900/50 bg-red-950/20 p-6">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div class="min-w-0">
                <h3 class="font-semibold text-red-300">Delete all data</h3>
                <p class="mt-1 max-w-prose text-sm leading-relaxed text-slate-400">
                  Removes every series and issue you've added, plus all publishers, creators, characters and genres.
                  Your account, password and photo stay. This can't be undone.
                </p>
              </div>
              <Button v-if="!confirmingDelete" type="button" label="Delete all data" icon="pi pi-trash" size="small"
                severity="danger" outlined class="shrink-0" @click="startDelete" />
            </div>

            <form v-if="confirmingDelete" class="mt-5 flex flex-col gap-3 border-t border-red-900/40 pt-5"
              @submit.prevent="deleteAllData">
              <label for="confirm-delete" class="text-sm text-slate-300">
                Type <span class="font-semibold text-slate-100">{{ original.username }}</span> to confirm
              </label>
              <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
                <InputText id="confirm-delete" ref="deleteInput" v-model="deleteConfirmation" autocomplete="off"
                  class="w-full sm:w-72" />
                <Button type="submit" label="Delete everything" size="small" severity="danger"
                  :disabled="deleteConfirmation !== original.username" :loading="deleting" />
                <Button type="button" label="Cancel" size="small" text severity="secondary" @click="cancelDelete" />
              </div>
            </form>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from "vue";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Select from "primevue/select";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import currencyCodes from "currency-codes";
import { useUserStore } from "@/store/user";
import type { User } from "@/types/user.types";
import AuthenticationService from "@/services/AuthenticationService";
import fallbackAvatar from "@/assets/user.svg";

const toast = useToast();
const userStore = useUserStore();


type ProfileFields = { username: string; email: string; currency: string };

const original = reactive<ProfileFields>({ username: "", email: "", currency: "" });
const form = reactive<ProfileFields>({ username: "", email: "", currency: "" });
const firstSeen = ref<string | null>(null);

const storedAvatar = ref("");                       
const avatarPreview = ref<string>(fallbackAvatar);
const pendingPhoto = ref<File | string | null>(null); 
const fileInput = ref<HTMLInputElement | null>(null);
const showLinkInput = ref(false);
const photoLink = ref("");
const savingProfile = ref(false);

const currencyOptions = Array.from(
  new Map(currencyCodes.data.map((c) => [c.code, c])).values()
)
  .filter((c) => !!c.code && !!c.currency)
  .map((c) => ({ code: c.code, name: c.currency }))
  .sort((a, b) => a.code.localeCompare(b.code));

const currencyByCode = new Map(currencyOptions.map((c) => [c.code, c.name]));
function currencyName(code: string) {
  return currencyByCode.get(code) || "";
}

const memberSince = computed(() => {
  if (!firstSeen.value) return "";
  const d = new Date(firstSeen.value);
  return Number.isNaN(d.getTime())
    ? ""
    : d.toLocaleDateString(undefined, { month: "long", year: "numeric" });
});

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

function applyUser(user: any) {
  original.username = user?.username || "";
  original.email = user?.email || "";
  original.currency = user?.preferred_currency || "USD";
  firstSeen.value = user?.first_seen || null;
  Object.assign(form, original);
}

function releaseStoredAvatar() {
  if (storedAvatar.value) URL.revokeObjectURL(storedAvatar.value);
  storedAvatar.value = "";
}

async function loadStoredAvatar(user: any) {
  releaseStoredAvatar();
  if (user?.profile_picture) {
    try {
      storedAvatar.value = await AuthenticationService.getUserPicture();
    } catch (e) {
      console.error("Failed to load profile picture:", e);
    }
  }
  avatarPreview.value = storedAvatar.value || fallbackAvatar;
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
    userStore.addUser(response.data);
    applyUser(response.data);
    pendingPhoto.value = null;
    photoLink.value = "";
    showLinkInput.value = false;
    if (photoChanged) await loadStoredAvatar(response.data);
    toast.add({ severity: "success", summary: "Saved", detail: "Your profile is up to date.", life: 3000 });
  } catch (error: any) {
    toast.add({ severity: "error", summary: "Couldn't save", detail: error.message, life: 5000 });
  } finally {
    savingProfile.value = false;
  }
}


const pw = reactive({ current: "", next: "", confirm: "" });
const changingPassword = ref(false);

const pwTooShort = computed(() => pw.next.length > 0 && pw.next.length < 3);
const pwMismatch = computed(() => pw.confirm.length > 0 && pw.next !== pw.confirm);
const canChangePassword = computed(
  () => !!pw.current && !!pw.next && !!pw.confirm && !pwTooShort.value && !pwMismatch.value
);

async function changePassword() {
  if (!canChangePassword.value) return;

  const data = new FormData();
  data.append("old_password", pw.current);
  data.append("password", pw.next);

  changingPassword.value = true;
  try {
    await AuthenticationService.updateUser(data);
    pw.current = "";
    pw.next = "";
    pw.confirm = "";
    toast.add({ severity: "success", summary: "Password changed", detail: "Use the new one next time you sign in.", life: 3000 });
  } catch (error: any) {
    toast.add({ severity: "error", summary: "Couldn't change password", detail: error.message, life: 5000 });
  } finally {
    changingPassword.value = false;
  }
}


const exporting = ref(false);
const confirmingDelete = ref(false);
const deleteConfirmation = ref("");
const deleteInput = ref<any>(null);
const deleting = ref(false);

async function exportCollection() {
  exporting.value = true;
  try {
    const data = await AuthenticationService.exportCollection();
    const url = window.URL.createObjectURL(new Blob([data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "vertigo-collection.xlsx");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    toast.add({ severity: "success", summary: "Download started", detail: "vertigo-collection.xlsx", life: 3000 });
  } catch {
    toast.add({ severity: "error", summary: "Export failed", detail: "The spreadsheet couldn't be generated. Try again.", life: 5000 });
  } finally {
    exporting.value = false;
  }
}

async function startDelete() {
  confirmingDelete.value = true;
  deleteConfirmation.value = "";
  await nextTick();
  deleteInput.value?.$el?.focus?.();
}

function cancelDelete() {
  confirmingDelete.value = false;
  deleteConfirmation.value = "";
}

async function deleteAllData() {
  if (deleteConfirmation.value !== original.username) return;

  deleting.value = true;
  try {
    const response = await AuthenticationService.deleteAllData();
    const seriesGone = response.data?.deleted?.series ?? 0;
    cancelDelete();
    toast.add({
      severity: "success",
      summary: "Deleted",
      detail: `${seriesGone} series and their issues are gone.`,
      life: 4000,
    });
  } catch {
    toast.add({ severity: "error", summary: "Couldn't delete", detail: "Nothing was removed. Try again.", life: 5000 });
  } finally {
    deleting.value = false;
  }
}


onMounted(async () => {
  let user = userStore.getUser();
  applyUser(user);

  try {
    const response = await AuthenticationService.getUser();
    const fresh: User = response.data;
    user = fresh;
    userStore.addUser(fresh);
    if (!profileDirty.value) applyUser(fresh);
  } catch (e) {
    console.error("Failed to refresh account details:", e);
  }
  await loadStoredAvatar(user);
});

onUnmounted(releaseStoredAvatar);
</script>

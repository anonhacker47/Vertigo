<template>
  <SettingsSection title="Integrations">
    <SettingsPanel as="form" @submit.prevent="saveToken">
      <template #header>
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 class="font-semibold text-slate-100">Metron</h3>
            <p class="mt-1 text-sm text-slate-400">Comic metadata from metron.cloud.</p>
          </div>
          <span :class="['pill', metronTone]">{{ metronPill }}</span>
        </div>
      </template>

      <div v-if="loading" class="flex items-center gap-2 text-sm text-slate-400">
        <i class="pi pi-spin pi-spinner"></i> Checking
      </div>

      <div v-else-if="loadError" class="flex flex-wrap items-center justify-between gap-3 text-sm text-slate-400">
        <span>{{ loadError }}</span>
        <Button type="button" label="Retry" size="small" text @click="loadStatus" />
      </div>

      <div v-else class="flex flex-col gap-6">
        <div v-if="metron?.configured"
          class="flex flex-col gap-3 rounded-lg border border-slate-800/60 bg-slate-950/40 px-4 py-3 sm:flex-row sm:items-center">
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-slate-200">{{ statusTitle }}</p>
            <p v-if="metron.source === 'server'" class="mt-0.5 text-xs text-slate-400">
              Add your own to use your account's quota.
            </p>
          </div>
          <Button type="button" label="Test connection" icon="pi pi-bolt" size="small" severity="secondary" outlined
            class="shrink-0" :loading="testing" @click="testConnection" />
        </div>

        <dl v-if="windows.length" class="grid gap-3 sm:grid-cols-2">
          <div v-for="w in windows" :key="w.label" class="rounded-lg border border-slate-800/60 px-4 py-3">
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500">{{ w.label }}</dt>
            <dd class="mt-1 text-sm text-slate-200">
              <span class="font-semibold tabular-nums">{{ w.remaining ?? '?' }}</span>
              <span class="text-slate-400"> of {{ w.limit?.toLocaleString() }} left</span>
            </dd>
            <dd v-if="w.reset" class="text-xs text-slate-500">Resets {{ w.reset }}</dd>
          </div>
        </dl>

        <div class="flex flex-col gap-1.5">
          <label for="metron-token" class="text-sm font-medium text-slate-300">API token</label>
          <Password inputId="metron-token" v-model="token" :feedback="false" toggleMask fluid autocomplete="off"
            placeholder="Paste your token" class="sm:max-w-md" :invalid="!!tokenError" />
          <p v-if="tokenError" class="text-xs text-red-400">{{ tokenError }}</p>
          <p class="text-xs text-slate-500">
            Create one on your
            <a href="https://metron.cloud/" target="_blank" rel="noopener noreferrer"
              class="text-sky-400 underline-offset-2 hover:underline">metron.cloud account</a>.
            Only the last four characters stay visible.
          </p>
        </div>
      </div>

      <template #footer>
        <template v-if="metron?.source === 'user'">
          <template v-if="confirmingRemove">
            <span class="mr-auto text-sm text-slate-400">
              Remove token? {{ metron.server_token ? "Imports will use the server's token." : "Comic imports will stop." }}
            </span>
            <Button type="button" label="Cancel" size="small" text severity="secondary" @click="confirmingRemove = false" />
            <Button type="button" label="Remove" size="small" severity="danger" :loading="removing" @click="removeToken" />
          </template>
          <Button v-else type="button" label="Remove" size="small" text severity="secondary" class="mr-auto"
            :disabled="saving" @click="confirmingRemove = true" />
        </template>
        <Button type="submit" label="Save" size="small" :loading="saving" :disabled="loading || !!loadError || !canSave" />
      </template>
    </SettingsPanel>

    <SettingsPanel>
      <template #header>
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 class="font-semibold text-slate-100">MyAnimeList</h3>
            <p class="mt-1 text-sm text-slate-400">Manga metadata via Tenrai's MyAnimeList mirror.</p>
          </div>
          <span class="pill pill--ok">Ready</span>
        </div>
      </template>
      <p class="text-sm text-slate-400">No account or key needed.</p>
    </SettingsPanel>
  </SettingsSection>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import Password from "primevue/password";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import IntegrationsService, { integrationErrorMessage } from "@/services/IntegrationsService";
import type { IntegrationsStatus, MetronRateLimit, MetronStatus } from "@/types/integrations.types";
import SettingsSection from "@/components/settings/SettingsSection.vue";
import SettingsPanel from "@/components/settings/SettingsPanel.vue";

const MIN_TOKEN_LENGTH = 8;

const toast = useToast();

const status = ref<IntegrationsStatus | null>(null);
const loading = ref(true);
const loadError = ref("");

const token = ref("");
const saving = ref(false);
const testing = ref(false);
const removing = ref(false);
const confirmingRemove = ref(false);

const metron = computed<MetronStatus | null>(() => status.value?.metron ?? null);

const canSave = computed(() => token.value.trim().length >= MIN_TOKEN_LENGTH);
const tokenError = computed(() => {
  const t = token.value.trim();
  return t.length > 0 && t.length < MIN_TOKEN_LENGTH ? "Too short for a Metron token." : "";
});

const metronPill = computed(() => {
  if (loading.value) return "Checking";
  if (loadError.value) return "Unknown";
  return metron.value?.configured ? "Connected" : "Not connected";
});
const metronTone = computed(() => {
  if (loading.value || loadError.value) return "pill--muted";
  return metron.value?.configured ? "pill--ok" : "pill--warn";
});

const statusTitle = computed(() =>
  metron.value?.source === "user" ? `Your token ${metron.value.token_hint ?? ""}` : "Server token"
);

function formatReset(iso: string | null) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const sameDay = d.toDateString() === new Date().toDateString();
  return sameDay
    ? `at ${d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    : d.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

const windows = computed(() => {
  const rl = metron.value?.rate_limit;
  if (!rl) return [];
  return [
    { label: "This minute", ...rl.burst },
    { label: "Today", ...rl.sustained },
  ]
    .filter((w) => w.limit != null)
    .map((w) => ({ ...w, reset: formatReset(w.reset) }));
});

function applyRateLimit(rateLimit: MetronRateLimit | null) {
  if (status.value && rateLimit) status.value.metron.rate_limit = rateLimit;
}

async function loadStatus() {
  loading.value = true;
  loadError.value = "";
  try {
    const res = await IntegrationsService.getStatus();
    status.value = res.data;
  } catch (error) {
    loadError.value = integrationErrorMessage(error, "Couldn't load status.");
  } finally {
    loading.value = false;
  }
}

async function saveToken() {
  if (!canSave.value || saving.value) return;
  saving.value = true;
  try {
    const res = await IntegrationsService.saveMetronToken(token.value.trim());
    status.value = res.data;
    token.value = "";
    confirmingRemove.value = false;
    toast.add({ severity: "success", summary: "Token saved", life: 3000 });
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Couldn't save token",
      detail: integrationErrorMessage(error, "Try again."),
      life: 6000,
    });
  } finally {
    saving.value = false;
  }
}

async function removeToken() {
  removing.value = true;
  try {
    const res = await IntegrationsService.clearMetronToken();
    status.value = res.data;
    confirmingRemove.value = false;
    toast.add({ severity: "success", summary: "Token removed", life: 3000 });
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Couldn't remove token",
      detail: integrationErrorMessage(error, "Try again."),
      life: 5000,
    });
  } finally {
    removing.value = false;
  }
}

async function testConnection() {
  testing.value = true;
  try {
    const res = await IntegrationsService.testMetron();
    applyRateLimit(res.data.rate_limit);
    const day = res.data.rate_limit?.sustained;
    const detail = day?.remaining != null && day.limit != null
      ? `${day.remaining.toLocaleString()} of ${day.limit.toLocaleString()} requests left today.`
      : undefined;
    toast.add({ severity: "success", summary: "Connected", detail, life: 4000 });
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Connection failed",
      detail: integrationErrorMessage(error, "Couldn't reach Metron. Try again shortly."),
      life: 6000,
    });
  } finally {
    testing.value = false;
  }
}

onMounted(loadStatus);
</script>

<style scoped>
.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}
.pill::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: currentColor;
}
.pill--ok { background: rgba(74, 222, 128, 0.12); color: #4ade80; }
.pill--warn { background: rgba(251, 191, 36, 0.12); color: #fbbf24; }
.pill--muted { background: rgba(148, 163, 184, 0.12); color: #94a3b8; }
</style>

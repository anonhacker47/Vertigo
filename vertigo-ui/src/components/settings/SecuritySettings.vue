<template>
  <SettingsSection title="Security" description="Keep your account yours.">
    <SettingsPanel as="form" title="Password" description="You'll stay signed in on this device after changing it."
      autocomplete="off" @submit.prevent="changePassword">
      <div class="flex flex-col gap-5 sm:max-w-sm">
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

      <template #footer>
        <Button type="submit" label="Change password" size="small" :loading="changingPassword"
          :disabled="!canChangePassword" />
      </template>
    </SettingsPanel>
  </SettingsSection>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from "vue";
import Password from "primevue/password";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import AuthenticationService from "@/services/AuthenticationService";
import SettingsSection from "@/components/settings/SettingsSection.vue";
import SettingsPanel from "@/components/settings/SettingsPanel.vue";

const toast = useToast();

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
</script>

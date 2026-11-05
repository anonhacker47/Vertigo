<template>
  <SettingsSection>
    <ExportPanel />
    <BackupPanel />
    <RestorePanel />
    <DeleteDataPanel />
  </SettingsSection>
</template>

<script setup lang="ts">
import SettingsSection from "@/components/settings/SettingsSection.vue";
import ExportPanel from "@/components/settings/ExportPanel.vue";
import BackupPanel from "@/components/settings/BackupPanel.vue";
import RestorePanel from "@/components/settings/RestorePanel.vue";
import DeleteDataPanel from "@/components/settings/DeleteDataPanel.vue";
</script>

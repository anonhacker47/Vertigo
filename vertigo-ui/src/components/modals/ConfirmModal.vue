<template>
  <ConfirmDialog>
    <template #message="slotProps">
      <p class="font-bold">{{ slotProps.message.message }}</p>
    </template>
  </ConfirmDialog>
</template>

<script setup lang="ts"></script>

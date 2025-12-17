<template>
    <ConfirmDialog >
    <template #message="slotProps">
        <p class="font-bold">
            Do you really want to delete the
            <span>{{ slotProps.message.message }}</span>?
        </p>
    </template>
    </ConfirmDialog>
</template>
<script setup>
</script>
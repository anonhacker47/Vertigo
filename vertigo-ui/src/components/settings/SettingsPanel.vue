<template>
  <component
    :is="as"
    :class="[
      'overflow-hidden rounded-xl border',
      danger ? 'border-red-900/50 bg-red-950/20' : 'border-slate-800/60 bg-slate-900/40',
    ]"
  >
    <div
      v-if="title || $slots.header"
      :class="['border-b px-6 py-4', danger ? 'border-red-900/40' : 'border-slate-800/60']"
    >
      <slot name="header">
        <h3 :class="['font-semibold', danger ? 'text-red-300' : 'text-slate-100']">{{ title }}</h3>
        <p v-if="description" class="mt-1 max-w-prose text-sm leading-relaxed text-slate-400">{{ description }}</p>
      </slot>
    </div>

    <div class="p-6">
      <slot />
    </div>

    <div
      v-if="$slots.footer"
      :class="[
        'flex flex-wrap items-center justify-end gap-2 border-t px-6 py-4',
        danger ? 'border-red-900/40' : 'border-slate-800/60',
      ]"
    >
      <slot name="footer" />
    </div>
  </component>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    description?: string;
    danger?: boolean;
    as?: "div" | "form";
  }>(),
  { as: "div" }
);
</script>

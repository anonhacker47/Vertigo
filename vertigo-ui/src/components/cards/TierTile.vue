<template>
  <div
    class="tier-tile relative group cursor-pointer shrink-0 aspect-2/3 rounded overflow-hidden border border-slate-700 hover:border-sky-400 transition-colors bg-slate-800"
    :title="`${item.label} (${item.rating || 'Unrated'} ⭐)`"
    @click="$emit('open')"
  >
    <img
      v-if="item.cover && !failed"
      :src="item.cover"
      :alt="item.label"
      crossorigin="anonymous"
      loading="lazy"
      decoding="async"
      class="w-full h-full object-cover pointer-events-none"
      @error="failed = true"
    />
    <div
      v-else
      class="w-full h-full flex items-center justify-center text-white pointer-events-none"
      :style="{ background: placeholderGradient(item.title) }"
      role="img"
      :aria-label="item.label"
    >
      <span class="text-base font-black tracking-wide drop-shadow">{{ placeholderInitials(item.title) }}</span>
    </div>

    <!-- Issues wear their number; several issues of one series can share the series cover. -->
    <span v-if="item.badge" class="tier-tile__badge">{{ item.badge }}</span>

    <div class="absolute bottom-0 left-0 right-0 bg-black/80 py-0.5 text-center opacity-0 group-hover:opacity-100 transition-opacity">
      <span class="text-[10px] font-bold text-yellow-400">{{ item.rating || '-' }} ⭐</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import type { TierItem } from "@/utils/tierListItems";
import { placeholderGradient, placeholderInitials } from "@/utils/placeholderGradient";

const props = defineProps<{ item: TierItem }>();
defineEmits<{ (e: "open"): void }>();

const failed = ref(false);
watch(() => props.item.cover, () => { failed.value = false; });
</script>

<style scoped>
.tier-tile__badge {
  position: absolute;
  top: 4px;
  left: 4px;
  z-index: 2;
  max-width: calc(100% - 8px);
  overflow: hidden;
  padding: 1px 6px;
  border-radius: 5px;
  background: rgba(11, 18, 32, 0.85);
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  line-height: 1.4;
  white-space: nowrap;
  text-overflow: ellipsis;
  pointer-events: none;
}
</style>

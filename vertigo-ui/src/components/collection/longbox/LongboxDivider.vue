<template>
  <!-- A longbox divider: the footprint of a comic, a little taller, with a tab on top. -->
  <div class="divider" aria-hidden="true">
    <span class="divider__tab">{{ label }}</span>
    <div class="divider__body">
      <span v-if="image && !failed" class="divider__plate">
        <img :src="image" alt="" decoding="async" draggable="false" @error="failed = true" />
      </span>
      <b v-else class="divider__mark">{{ label }}</b>
      <span v-if="image && !failed" class="divider__name">{{ label }}</span>
      <span class="divider__count">{{ count }} series</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

const props = withDefaults(defineProps<{ label: string; count: number; image?: string | null }>(), { image: null });

const failed = ref(false);
watch(() => props.image, () => { failed.value = false; });
</script>

<style scoped>
/*
 * Painted, not frosted: a backdrop blur would re-render the scene behind the tab on every frame
 * the row moves, which is what made the dividers flicker.
 */
.divider {
  position: relative;
  /* --w is the cover width set by the stage; the card sits a little inside a cover's outline, tab included */
  width: 92%;
  height: calc(var(--w, 210px) * 1.38);
  margin: 0 auto;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: linear-gradient(180deg, rgb(51, 65, 85), rgb(30, 41, 59));
  box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.5);
}
.divider__tab {
  position: absolute;
  left: 12px;
  top: -23px;
  height: 24px;
  max-width: calc(100% - 24px);
  padding: 0 12px;
  overflow: hidden;
  border-radius: 6px 6px 0 0;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-bottom: 0;
  background: rgb(71, 85, 105);
  color: #fff;
  font-size: 11px;
  font-weight: 900;
  line-height: 24px;
  letter-spacing: 0.01em;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.divider__body {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 18px;
}
/* a white plate so any publisher mark, light or dark, reads */
.divider__plate {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72%;
  aspect-ratio: 1;
  padding: 12%;
  border-radius: 12px;
  background: #fff;
}
.divider__plate img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.divider__mark {
  font-size: 26px;
  font-weight: 900;
  line-height: 1.1;
  text-align: center;
  color: #fff;
  overflow-wrap: anywhere;
}
.divider__name {
  font-size: 14px;
  font-weight: 900;
  line-height: 1.2;
  text-align: center;
  color: #fff;
  overflow-wrap: anywhere;
}
.divider__count {
  font-size: 12px;
  font-weight: 700;
  color: #94a3b8;
}
</style>

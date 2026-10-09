<template>
  <li class="flex min-w-0 flex-col gap-2">
    <RouterLink :to="to" class="block" :aria-label="series.display_title">
      <CoverImage :src="cover ?? series.cover" :title="series.title" :alt="series.display_title" initials-class="text-3xl" />
    </RouterLink>
    <RouterLink :to="to" class="line-clamp-1 text-sm font-bold leading-5 text-white hover:text-sky-300">
      {{ series.display_title }}
    </RouterLink>
    <slot />
  </li>
</template>

<script setup lang="ts">
import { computed } from "vue";
import CoverImage from "@/components/common/CoverImage.vue";
import type { SeriesBasics } from "@/types/insights.types";

const props = defineProps<{ series: SeriesBasics; cover?: string | null }>();

const to = computed(() => ({ name: "SeriesDetail", params: { Id: props.series.id, Link: props.series.slug } }));
</script>

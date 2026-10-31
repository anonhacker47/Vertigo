<template>
  <li class="flex min-w-0 flex-col gap-2">
    <RouterLink :to="coverTo" class="block" :aria-label="coverLabel">
      <CoverImage :src="issue?.cover ?? series.cover" :title="series.title" :alt="coverLabel" initials-class="text-3xl" />
    </RouterLink>
    <RouterLink :to="seriesTo" class="line-clamp-1 text-sm font-bold leading-5 text-white hover:text-sky-300">
      {{ series.display_title }}
    </RouterLink>
    <slot />
  </li>
</template>

<script setup lang="ts">
import { computed } from "vue";
import CoverImage from "@/components/common/CoverImage.vue";
import type { IssueBasics, SeriesBasics } from "@/types/insights.types";
const props = defineProps<{ series: SeriesBasics; issue?: IssueBasics | null }>();

const seriesTo = computed(() => ({ name: "SeriesDetail", params: { Id: props.series.id, Link: props.series.slug } }));
const coverTo = computed(() =>
  props.issue
    ? { name: "IssueDetail", params: { seriesId: props.series.id, slug: props.series.slug, number: props.issue.number } }
    : seriesTo.value,
);
const coverLabel = computed(() => (props.issue ? `${props.series.display_title} #${props.issue.number}` : props.series.display_title));
</script>

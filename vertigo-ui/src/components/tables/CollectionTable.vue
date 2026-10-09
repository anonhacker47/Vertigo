<template>
  <div class="overflow-x-auto rounded-lg border border-white/8">
    <table class="w-full text-sm">
      <thead>
        <tr class="text-left text-[12px] font-bold text-slate-400">
          <th class="px-4 py-3">Series</th>
          <th class="hidden px-4 py-3 md:table-cell">Publisher</th>
          <th class="hidden px-4 py-3 md:table-cell">Format</th>
          <th class="hidden px-4 py-3 md:table-cell">Added</th>
          <th class="hidden px-4 py-3 md:table-cell">Rating</th>
          <th class="px-4 py-3 text-right">Owned</th>
          <th class="px-4 py-3 text-right">Read</th>
          <th v-if="deleteMode" class="w-14 px-2 py-3"><span class="sr-only">Delete</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="series in seriesList" :key="series.id" class="row border-t border-white/6"
          :class="{ 'cursor-pointer': !deleteMode }" @click="open(series)">
          <td class="max-w-xs px-4 py-2">
            <div class="flex items-center gap-3">
              <img :src="cover(series)" loading="lazy" decoding="async" width="40" height="60" alt=""
                class="h-15 w-10 shrink-0 rounded-sm bg-slate-800 object-cover" @error="onCoverError" />
              <RouterLink :to="route(series)" class="truncate font-bold text-white hover:underline" @click.stop>
                {{ series.title }}
              </RouterLink>
            </div>
          </td>
          <td class="hidden px-4 py-2 text-slate-300 md:table-cell">
            <span v-if="series.publisher?.title">{{ series.publisher.title }}</span>
            <span v-else class="text-slate-600">—</span>
          </td>
          <td class="hidden px-4 py-2 text-slate-300 md:table-cell">{{ series.series_format }}</td>
          <td class="hidden whitespace-nowrap px-4 py-2 text-slate-400 md:table-cell">{{ added(series) }}</td>
          <td class="hidden px-4 py-2 md:table-cell">
            <span class="inline-flex gap-0.5" role="img" :aria-label="`${series.user_rating || 0} of 5 stars`">
              <i v-for="n in 5" :key="n" class="pi text-[11px]"
                :class="n <= (series.user_rating || 0) ? 'pi-star-fill text-sky-400' : 'pi-star text-slate-600'"></i>
            </span>
          </td>
          <td class="whitespace-nowrap px-4 py-2 text-right tabular-nums text-slate-200">
            {{ series.owned_count }}<span class="text-slate-500"> / {{ series.issue_count }}</span>
          </td>
          <td class="whitespace-nowrap px-4 py-2 text-right tabular-nums text-slate-200">
            {{ series.read_count }}<span class="text-slate-500"> / {{ series.issue_count }}</span>
          </td>
          <td v-if="deleteMode" class="px-2 py-2 text-center">
            <button type="button" class="del" :aria-label="`Delete ${series.title}`"
              @click.stop="confirmDelete(series.id, series.title)">
              <i class="pi pi-trash"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import SeriesService from "@/services/SeriesService";
import type { Series } from "@/types/series.types";
import fallbackCover from "@/assets/dummy.webp";

const props = defineProps<{
  seriesList: Series[];
  deleteMode: boolean;
  confirmDelete: (id: number, title: string) => void;
}>();

const router = useRouter();

// One formatter for the whole table; building one per row is measurably slow.
const dateFormat = new Intl.DateTimeFormat("en-US", { day: "numeric", month: "short", year: "numeric" });

function added(series: Series) {
  const d = new Date(series.timestamp);
  return Number.isNaN(d.getTime()) ? "" : dateFormat.format(d);
}

function cover(series: Series) {
  return SeriesService.getSeriesImageById(series.id, series.last_updated);
}

function onCoverError(event: Event) {
  (event.target as HTMLImageElement).src = fallbackCover;
}

function route(series: Series) {
  return { name: "SeriesDetail", params: { Link: series.slug, Id: series.id } };
}

function open(series: Series) {
  if (props.deleteMode) return;
  router.push(route(series));
}
</script>

<style scoped>
.row {
  transition: background-color 0.12s ease;
}
.row:hover {
  background: rgba(255, 255, 255, 0.04);
}
.del {
  display: inline-flex;
  width: 32px;
  height: 32px;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  color: #f87171;
  transition: background-color 0.12s ease, color 0.12s ease;
}
.del:hover {
  background: rgba(220, 38, 38, 0.15);
  color: #fff;
}
.del:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
}
</style>

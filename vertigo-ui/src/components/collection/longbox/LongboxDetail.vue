<template>
  <aside class="detail" aria-live="polite">
    <Transition name="swap" mode="out-in">
      <div v-if="series" :key="'s' + series.id" class="detail__body">
        <div>
          <h2 class="detail__title" :title="series.title">
            <RouterLink :to="seriesRoute(series)">{{ series.title }}</RouterLink>
          </h2>
          <p class="detail__meta">
            <RouterLink v-if="series.publisher" :to="`/publisher/${series.publisher.id}-${series.publisher.slug}`" class="meta-link">{{ series.publisher.title }}</RouterLink>
            <template v-if="series.publisher && series.series_format"> · </template>
            <RouterLink v-if="series.series_format" :to="{ path: '/collection', query: { series_format: series.series_format } }" class="meta-link">{{ series.series_format }}</RouterLink>
            <template v-if="startedYear"> · started {{ startedYear }}</template>
          </p>
        </div>

        <div class="tracks">
          <div class="track">
            <div class="track__row">Owned <span class="num">{{ series.owned_count }} of {{ series.issue_count }}</span></div>
            <div class="bar"><i class="bar__owned" :style="{ width: share(series.owned_count, series.issue_count) }"></i></div>
          </div>
          <div class="track">
            <div class="track__row">Read <span class="num">{{ series.read_count }} of {{ series.issue_count }}</span></div>
            <div class="bar"><i class="bar__read" :style="{ width: share(series.read_count, series.issue_count) }"></i></div>
          </div>
        </div>

        <div class="facts">
          <div><b class="num">{{ missing }}</b><span>{{ missing === 1 ? "issue missing" : "issues missing" }}</span></div>
          <div><b class="num">{{ unread }}</b><span>unread on the shelf</span></div>
          <div>
            <b class="stars" role="img" :aria-label="`${rating} of 5 stars`">
              <i v-for="n in 5" :key="n" class="pi" :class="n <= rating ? 'pi-star-fill stars__on' : 'pi-star stars__off'"></i>
            </b>
            <span>{{ rating ? "your rating" : "not rated yet" }}</span>
          </div>
        </div>

        <div class="tags">
          <TagLink v-for="genre in genres" :key="genre" :label="genre" :to="{ path: '/collection', query: { genre } }" />
          <TagLink v-for="creator in creators" :key="creator.id || creator.title" :label="creator.title" :to="`/creator/${creator.id}-${creator.slug}`" />
        </div>

        <div class="cta">
          <RouterLink :to="seriesRoute(series)" custom v-slot="{ navigate }">
            <Button label="Open series" icon="pi pi-arrow-right" icon-pos="right" size="small" @click="navigate" />
          </RouterLink>
          <RouterLink :to="{ name: 'EditSeries', params: { Link: series.slug, Id: series.id } }" custom v-slot="{ navigate }">
            <Button label="Edit" severity="secondary" size="small" @click="navigate" />
          </RouterLink>
          <Button v-if="deleteMode" label="Delete" icon="pi pi-trash" severity="danger" size="small" @click="$emit('confirmDelete', series.id, series.title)" />
        </div>
      </div>

      <div v-else-if="divider" :key="'d' + divider.id" class="detail__body">
        <div>
          <h2 class="detail__title">{{ divider.label }}</h2>
          <p class="detail__meta">{{ divider.series.length }} series behind this tab</p>
        </div>
        <div class="facts facts--four">
          <div><b class="num">{{ totals.issues }}</b><span>issues</span></div>
          <div><b class="num">{{ totals.owned }}</b><span>owned</span></div>
          <div><b class="num">{{ totals.read }}</b><span>read</span></div>
          <div><b class="num">{{ totals.issues - totals.owned }}</b><span>missing</span></div>
        </div>
        <ul class="chips">
          <li v-for="s in divider.series.slice(0, 8)" :key="s.id" class="chip">{{ s.title }}</li>
          <li v-if="divider.series.length > 8" class="chip">+{{ divider.series.length - 8 }} more</li>
        </ul>
      </div>

      <p v-else class="detail__empty">Nothing in the box.</p>
    </Transition>
  </aside>
</template>

<script setup lang="ts">
import { computed } from "vue";
import Button from "primevue/button";
import TagLink from "@/components/common/TagLink.vue";
import type { Series } from "@/types/series.types";
import { groupTotals, type LongboxItem } from "./dividers";

const props = defineProps<{ item: LongboxItem | null; deleteMode: boolean }>();
defineEmits<{ (e: "confirmDelete", id: number, title: string): void }>();

const series = computed(() => (props.item?.kind === "series" ? props.item.series : null));
const divider = computed(() => (props.item?.kind === "divider" ? props.item : null));

const startedYear = computed(() => {
  if (!series.value?.release_date) return null;
  const year = new Date(series.value.release_date).getFullYear();
  return Number.isNaN(year) ? null : year;
});
const missing = computed(() => Math.max(0, (series.value?.issue_count || 0) - (series.value?.owned_count || 0)));
const unread = computed(() => Math.max(0, (series.value?.owned_count || 0) - (series.value?.read_count || 0)));
const rating = computed(() => Math.round(series.value?.user_rating || 0));
const genres = computed(() => (series.value?.genre ?? []).slice(0, 4));
const creators = computed(() => (series.value?.creator ?? []).slice(0, 4));
const totals = computed(() => groupTotals(divider.value?.series ?? []));

const share = (count: number, total: number) => `${total ? Math.min(100, (count / total) * 100) : 0}%`;
const seriesRoute = (s: Series) => ({ name: "SeriesDetail", params: { Link: s.slug, Id: s.id } });
</script>

<style scoped>
/*
 * A text column beside the stage, no card around it: the glow is the backdrop. It is as tall as
 * the stage and every block in it has a fixed height, so riffling never moves anything.
 */
.detail {
  display: flex;
  flex-direction: column;
  min-width: 0;
  height: var(--lb-h, 480px);
  padding: 36px 0 24px;
  overflow: hidden;
}
/* a shorter window gets a shorter stage, so the column tightens to keep its buttons in view */
@media (max-height: 800px) {
  .detail { padding: 20px 0 12px; }
  .detail__body { gap: 12px; }
  .detail__title { font-size: 28px; }
  .facts > div { min-height: 54px; }
}
/* stacked under the stage on a phone: content-sized, buttons right after the tags */
@media (max-width: 767px) {
  .detail { height: auto; min-height: 0; padding: 0; }
  .detail__body { gap: 16px; }
  .detail__title { font-size: 26px; }
  .facts { gap: 12px; }
  .cta { margin-top: 0; }
}
.detail__body {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
  min-height: 0;
}
/* every block keeps its height; the column is sized so they all fit, and nothing gets squeezed */
.detail__body > * { flex-shrink: 0; }
.detail__title {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  margin: 0;
  min-height: 2.1em;
  font-size: 34px;
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: #fff;
  overflow-wrap: anywhere;
}
.detail__title a:hover { color: #7dd3fc; }
.detail__meta {
  margin: 10px 0 0;
  overflow: hidden;
  font-size: 13px;
  font-weight: 700;
  color: #94a3b8;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.detail__empty {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #94a3b8;
}
.meta-link { color: #cbd5e1; }
.meta-link:hover { color: #fff; text-decoration: underline; text-underline-offset: 3px; }
.num { font-variant-numeric: tabular-nums; }

.tracks { display: flex; flex-direction: column; gap: 12px; }
.track { display: flex; flex-direction: column; gap: 7px; }
.track__row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 13px;
  font-weight: 700;
  color: #cbd5e1;
}
.track__row span { color: #94a3b8; }
.bar {
  height: 6px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
}
.bar i { display: block; height: 100%; border-radius: 999px; transition: width 0.45s ease; }
.bar__owned { background: #0ea5e9; }
.bar__read { background: #4ade80; }

.facts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.facts--four { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.facts > div { min-height: 62px; }
.facts b { display: block; font-size: 24px; font-weight: 900; line-height: 1.1; color: #fff; }
.facts span { display: block; margin-top: 2px; font-size: 12px; font-weight: 700; line-height: 1.3; color: #94a3b8; }
.stars { display: inline-flex; gap: 2px; height: 26px; align-items: center; }
.stars i { font-size: 13px; }
.stars__on { color: #38bdf8; }
.stars__off { color: #475569; }

.tags { display: flex; flex-wrap: wrap; align-content: flex-start; gap: 8px; height: 32px; overflow: hidden; }
.cta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: auto; padding-top: 4px; }

.chips { display: flex; flex-wrap: wrap; align-content: flex-start; gap: 6px; max-height: 96px; margin: 0; padding: 0; overflow: hidden; list-style: none; }
.chip {
  display: inline-flex;
  align-items: center;
  height: 26px;
  max-width: 100%;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 12px;
  font-weight: 800;
  color: #cbd5e1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* the column swaps with a short settle when the front cover changes */
.swap-enter-active { transition: opacity 0.2s ease-out, transform 0.2s ease-out; }
.swap-leave-active { transition: opacity 0.12s ease-in; }
.swap-enter-from { opacity: 0; transform: translateY(6px); }
.swap-leave-to { opacity: 0; }
@media (prefers-reduced-motion: reduce) {
  .bar i,
  .swap-enter-active,
  .swap-leave-active { transition: none; }
}
</style>

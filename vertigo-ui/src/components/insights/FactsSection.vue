<template>
  <section v-if="loading || cards.length" id="facts" class="scroll-mt-[calc(var(--spacing-header)+1rem)] mx-auto mt-14 w-full max-w-7xl px-4 md:mt-16 md:px-8" aria-labelledby="facts-title">
    <SectionHead title="Did you know" subtitle="changes daily" />

    <Skeleton v-if="loading" variant="lines" :count="3" />

    <p v-else-if="error" class="py-6 text-slate-400">
      {{ error }} <button class="font-bold text-sky-400 hover:text-sky-300" type="button" @click="reload">Try again</button>
    </p>

    <div v-else class="flex flex-wrap gap-4">
      <article
        v-for="card in cards"
        :key="card.key"
        class="fact relative min-w-0 grow basis-[340px] overflow-hidden rounded-2xl border border-white/[.08] bg-slate-900"
      >
        <img v-if="card.cover && !card.swatches" :src="card.cover" alt="" class="fact__wash" aria-hidden="true" />
        <div v-else class="fact__wash" :style="{ background: card.swatches ? swatchGradient(card.swatches) : placeholderGradient(card.coverTitle) }" aria-hidden="true"></div>
        <div class="fact__scrim" aria-hidden="true"></div>
        <div class="relative flex items-center gap-5 p-5">
          <div v-if="card.swatches" class="fact__swatches" aria-hidden="true">
            <i v-for="(c, i) in card.swatches" :key="i" class="block" :style="{ background: c }"></i>
          </div>
          <CoverImage v-else :src="card.cover" :title="card.coverTitle" :aspect="false" depth="md" :interactive="false" initials-class="text-xl" class="h-[132px] w-[88px] shrink-0" />
          <div class="flex min-h-[132px] min-w-0 flex-col">
            <p class="text-xs font-bold text-sky-300">{{ card.kicker }}</p>
            <h3 class="mt-1 text-[17px] font-extrabold leading-snug text-white">{{ card.headline }}</h3>
            <p class="mt-1.5 text-sm font-semibold text-slate-200">{{ card.detail }}</p>
            <RouterLink v-if="card.to" :to="card.to" class="mt-auto pt-3 text-[13px] font-bold text-sky-300 hover:text-white">{{ card.cta }}</RouterLink>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";
import InsightsService from "@/services/InsightsService";
import { useInsightsSection } from "@/composables/useInsightsSection";
import { formatDate } from "@/utils/relativeTime";
import { placeholderGradient } from "@/utils/placeholderGradient";
import SectionHead from "./SectionHead.vue";
import CoverImage from "@/components/common/CoverImage.vue";
import Skeleton from "./Skeleton.vue";
import type { Fact, FactLink, OnThisDay } from "@/types/insights.types";

const { data, loading, error, reload } = useInsightsSection(() => InsightsService.getFacts());

interface Card {
  key: string;
  kicker: string;
  headline: string;
  detail: string;
  cover: string | null;
  coverTitle: string;
  swatches?: string[];
  to: RouteLocationRaw | null;
  cta: string;
}

function linkTo(link: FactLink | null): { to: RouteLocationRaw | null; cta: string } {
  if (!link) return { to: null, cta: "" };
  switch (link.kind) {
    case "issue":
      return { to: { name: "IssueDetail", params: { seriesId: link.series_id, slug: link.slug, number: link.number } }, cta: "Open issue" };
    case "series":
      return { to: { name: "SeriesDetail", params: { Id: link.id, Link: link.slug } }, cta: "Open series" };
    case "creator":
      return { to: `/creator/${link.id}-${link.slug}`, cta: "Open creator" };
    case "publisher":
      return { to: `/publisher/${link.id}-${link.slug}`, cta: "Open publisher" };
    default:
      return { to: "/collection", cta: "Open collection" };
  }
}

function onThisDayCards(otd: OnThisDay): Card[] {
  const cards: Card[] = [];
  const when = otd.scope === "day" ? "On this day" : "This week";
  for (const group of otd.groups) {
    const first = group.items[0];
    const verb = group.kind === "bought" ? "bought" : "finished";
    const names = group.items.map((i) => i.label);
    const headline = group.count > 1 ? `You ${verb} ${group.count} books` : `You ${verb} ${first.label}`;
    const detail = group.count > 1
      ? `${names.slice(0, 2).join(", ")}${group.count > 2 ? ` and ${group.count - 2} more` : ""}. ${formatDate(group.date)}.`
      : `${formatDate(group.date)}.${group.kind === "bought" && !first.issue.is_read ? " Still unread." : ""}`;
    const link = group.count === 1
      ? linkTo({ kind: "issue", series_id: first.series.id, slug: first.series.slug, number: first.issue.number })
      : { to: null, cta: "" };
    cards.push({ key: `otd-${group.kind}-${group.year}`, kicker: `${when} in ${group.year}`, headline, detail, cover: first.issue.cover, coverTitle: first.series.title, ...link });
  }
  if (otd.anniversary) {
    const y = otd.anniversary.years;
    cards.push({ key: "otd-anniversary", kicker: "Anniversary", headline: `${y === 1 ? "One year" : `${y} years`} ago today you started this shelf`, detail: `On Vertigo since ${formatDate(otd.anniversary.since)}.`, cover: null, coverTitle: "Vertigo", to: "/collection", cta: "Open collection" });
  }
  return cards;
}

function factCard(fact: Fact): Card {
  return { key: fact.id, kicker: fact.kicker, headline: fact.headline, detail: fact.detail, cover: fact.cover, coverTitle: fact.headline, swatches: fact.swatches, ...linkTo(fact.link) };
}

function swatchGradient(colors: string[]): string {
  return `linear-gradient(135deg, ${colors.join(", ")})`;
}

const cards = computed<Card[]>(() => {
  if (!data.value) return [];
  return [...(data.value.on_this_day ? onThisDayCards(data.value.on_this_day) : []), ...data.value.facts.map(factCard)];
});
</script>

<style scoped>
/* Each fact is washed with its own cover, the same device as the hero. */
.fact__wash {
  position: absolute;
  inset: -25%;
  width: 150%;
  height: 150%;
  object-fit: cover;
  filter: blur(40px) saturate(0.9);
  opacity: 0.22;
  pointer-events: none;
}
.fact__scrim {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(90deg, rgba(15, 23, 42, 0.5) 0%, rgba(15, 23, 42, 0.25) 100%);
}
.fact__swatches {
  display: grid;
  grid-template-rows: repeat(3, 1fr);
  flex: none;
  width: 88px;
  gap: 3px;
  height: 132px;
  overflow: hidden;
  border-radius: 2px 6px 6px 2px;
  box-shadow: -4px 2px 4px 0 rgba(0, 0, 0, 0.3), -8px 8px 20px 0 rgba(0, 0, 0, 0.2);
}
</style>

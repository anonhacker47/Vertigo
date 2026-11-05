import type { Series } from "@/types/series.types";
import PublisherService from "@/services/PublisherService";

export interface LongboxDivider {
  kind: "divider";
  id: string;
  label: string;
  image: string | null;
  series: Series[];
}
export interface LongboxSeries {
  kind: "series";
  id: string;
  series: Series;
}
export type LongboxItem = LongboxDivider | LongboxSeries;

interface Rule {
  label: (series: Series) => string;
  image?: (series: Series) => string | null;
}

const monthFormat = new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric" });

function firstLetter(series: Series): string {
  const ch = (series.title ?? "").trim().charAt(0).toUpperCase();
  if (/[0-9]/.test(ch)) return "0–9";
  return /[A-Z]/.test(ch) ? ch : "#";
}

function addedMonth(series: Series): string {
  const date = new Date(series.timestamp);
  return Number.isNaN(date.getTime()) ? "Unknown date" : monthFormat.format(date);
}

function stars(series: Series): string {
  const n = Math.round(series.user_rating || 0);
  return n ? `${n} star${n === 1 ? "" : "s"}` : "Not rated";
}


const RULES: Record<string, Rule> = {
  title: { label: firstLetter },
  publisher: {
    label: (series) => series.publisher?.title || "No publisher",
    image: (series) => (series.publisher?.id ? PublisherService.getPublisherImageById(series.publisher.id) : null),
  },
  series_format: { label: (series) => series.series_format || "No format" },
  timestamp: { label: addedMonth },
  user_rating: { label: stars },
};

export function buildLongboxItems(seriesList: Series[], orderBy: string): LongboxItem[] {
  const rule = RULES[orderBy];
  if (!rule) return seriesList.map((series) => ({ kind: "series", id: `s${series.id}`, series }));

  const items: LongboxItem[] = [];
  let open: LongboxDivider | null = null;
  for (const [index, series] of seriesList.entries()) {
    const label = rule.label(series);
    if (!open || open.label !== label) {
      open = { kind: "divider", id: `d${index}`, label, image: rule.image?.(series) ?? null, series: [] };
      items.push(open);
    }
    open.series.push(series);
    items.push({ kind: "series", id: `s${series.id}`, series });
  }
  return items;
}

export function groupTotals(series: Series[]) {
  return series.reduce(
    (totals, s) => ({
      issues: totals.issues + (s.issue_count || 0),
      owned: totals.owned + (s.owned_count || 0),
      read: totals.read + (s.read_count || 0),
    }),
    { issues: 0, owned: 0, read: 0 }
  );
}

/**
 * What the tier list ranks. Series and issues are flattened to one shape so the view,
 * the saved layout and the image export never need to know which mode is on.
 */
import type { RouteLocationRaw } from "vue-router";
import SeriesService from "@/services/SeriesService";
import IssueService from "@/services/IssueService";
import type { Series } from "@/types/series.types";
import type { LibraryIssue } from "@/types/issue.types";
import { hasCustomIssueTitle, issueNumberLabel } from "@/utils/issueTitle";

export type TierListMode = "series" | "issues";

export interface TierItem {
  /** Unique within a mode; what the saved layout records. */
  id: number;
  /** Full label for tooltips and alt text, e.g. "Hellblazer #41". */
  label: string;
  /** Series title; seeds the cover placeholder. */
  title: string;
  /** Lower-cased text the deck search matches against. */
  searchText: string;
  rating: number | null;
  cover: string | null;
  /** Small corner chip ("#41" for issues); series have none. */
  badge?: string;
  route: RouteLocationRaw;
}

export const TIER_LIST_MODES: { label: string; value: TierListMode }[] = [
  { label: "Series", value: "series" },
  { label: "Issues", value: "issues" },
];

const NO_IMAGE = "noimage";

// The list endpoints cap a page at these sizes; see paginated_response in the backend.
const SERIES_PAGE = 100;
const ISSUES_PAGE = 500;

function seriesCover(id: number, thumbnail: unknown, lastUpdated?: string | null): string | null {
  if (!thumbnail || thumbnail === NO_IMAGE) return null;
  return SeriesService.getSeriesImageById(id, lastUpdated ?? undefined);
}

function entityTitles(refs: unknown): string[] {
  if (!Array.isArray(refs)) return [];
  return refs.map((r) => (typeof r === "string" ? r : r?.title ?? "")).filter(Boolean);
}

export function seriesTierItem(series: Series): TierItem {
  return {
    id: series.id,
    label: series.title,
    title: series.title,
    searchText: [series.title, ...entityTitles(series.creator)].join(" ").toLowerCase(),
    rating: series.user_rating ?? null,
    cover: seriesCover(series.id, series.thumbnail, series.last_updated),
    route: { name: "SeriesDetail", params: { Id: String(series.id), Link: series.slug } },
  };
}

export function issueTierItem(issue: LibraryIssue): TierItem {
  const number = issueNumberLabel(issue.number, issue.title);
  const label = hasCustomIssueTitle(issue.title, issue.number)
    ? `${issue.series.title} ${number} · ${issue.title}`
    : `${issue.series.title} ${number}`;
  return {
    id: issue.id,
    label,
    title: issue.series.title,
    searchText: label.toLowerCase(),
    rating: issue.user_rating ?? null,
    // The issue's own cover wins; otherwise the series cover stands in, as on the series page.
    cover: issue.thumbnail
      ? IssueService.getIssueImageById(issue.id, issue.last_updated)
      : seriesCover(issue.series.id, issue.series.thumbnail, issue.series.last_updated),
    badge: number,
    route: {
      name: "IssueDetail",
      params: { seriesId: String(issue.series.id), slug: issue.series.slug, number: String(issue.number) },
    },
  };
}

/** Pages through a capped list endpoint until it has everything. */
async function pageAll<T>(
  pageSize: number,
  fetchPage: (limit: number, offset: number) => Promise<{ items: T[]; total: number }>,
): Promise<T[]> {
  const all: T[] = [];
  let offset = 0;
  for (;;) {
    const { items, total } = await fetchPage(pageSize, offset);
    all.push(...items);
    offset += items.length;
    if (items.length === 0 || offset >= total) return all;
  }
}

/** Every rankable item for a mode, in the order the deck shows them before any ranking. */
export async function loadTierItems(mode: TierListMode): Promise<TierItem[]> {
  if (mode === "issues") {
    const issues = await pageAll<LibraryIssue>(ISSUES_PAGE, async (limit, offset) => {
      const { issuesList, pagination } = await IssueService.fetchUserIssues(limit, offset);
      return { items: issuesList, total: pagination.total };
    });
    issues.sort((a, b) => a.series.title.localeCompare(b.series.title) || a.number - b.number);
    return issues.map(issueTierItem);
  }
  const series = await pageAll<Series>(SERIES_PAGE, async (limit, offset) => {
    const { seriesList, pagination } = await SeriesService.fetchSeries("title", "asc", limit, offset);
    return { items: seriesList, total: pagination.total };
  });
  return series.map(seriesTierItem);
}

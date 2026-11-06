import getSymbolFromCurrency from "currency-symbol-map";
import CharacterService from "@/services/CharacterService";
import DashboardService from "@/services/DashboardService";
import InsightsService from "@/services/InsightsService";
import IssueService from "@/services/IssueService";
import SeriesService from "@/services/SeriesService";
import { useUserStore } from "@/store/user";
import type { Entity } from "@/types/entity.types";
import type { LibraryIssue } from "@/types/issue.types";
import type { Series } from "@/types/series.types";

/** What the room needs to know about a series: enough for a cover, a spine colour and the card. */
export interface RoomSeries {
  kind: "series";
  id: number;
  title: string;
  slug: string;
  publisher: string;
  format: string;
  year: number | null;
  genre: string[];
  creators: string[];
  rating: number;
  issues: number;
  owned: number;
  read: number;
  rgb: [number, number, number];
  cover: string;
}

/** The room has shelf space for this many; the rest are the longboxes under the desk. */
export const ROOM_MAX_SERIES = 260;
const PAGE = 100;

export function rgbOf(value: unknown): [number, number, number] | null {
  if (Array.isArray(value) && value.length >= 3) return [Number(value[0]), Number(value[1]), Number(value[2])];
  const m = String(value ?? "").match(/(\d+)\D+(\d+)\D+(\d+)/);
  return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
}

function toRoomSeries(s: Series): RoomSeries {
  return {
    kind: "series",
    id: s.id,
    title: s.title,
    slug: s.slug,
    publisher: s.publisher?.title ?? "",
    format: s.series_format ?? "",
    year: s.release_date ? new Date(s.release_date).getFullYear() : null,
    genre: s.genre ?? [],
    creators: (s.creator ?? []).map((c) => c.title),
    rating: Number(s.user_rating) || 0,
    issues: s.issue_count ?? 0,
    owned: s.owned_count ?? 0,
    read: s.read_count ?? 0,
    rgb: rgbOf(s.dominant_color) ?? [90, 90, 110],
    cover: SeriesService.getSeriesImageById(s.id, s.thumbnail_updated ?? s.last_updated ?? undefined),
  };
}

/** The most recently added series, newest first, up to the room's capacity. */
export async function loadRoomSeries(): Promise<{ series: RoomSeries[]; total: number }> {
  const first = await SeriesService.fetchSeries("timestamp", "desc", PAGE, 0);
  let list = first.seriesList;
  const total: number = first.pagination?.total ?? list.length;
  for (let offset = PAGE; offset < Math.min(total, ROOM_MAX_SERIES); offset += PAGE) {
    const page = await SeriesService.fetchSeries("timestamp", "desc", PAGE, offset);
    list = list.concat(page.seriesList);
  }
  return { series: list.slice(0, ROOM_MAX_SERIES).map(toRoomSeries), total };
}

/** What the plaque in the room's secret says: the total spent, with two figures under it. */
export interface RoomSummary {
  spent: number;
  symbol: string;
  issues: number;
  series: number;
  since: number | null;
}

/** The totals behind the plaque. Any part that fails falls back to what the room already counted. */
export async function loadRoomSummary(fallback: { series: number; issues: number }): Promise<RoomSummary> {
  const [spent, records, seriesStats, issueStats] = await Promise.all([
    DashboardService.getTotalSpent().then((r) => Number(r.data?.totalSpent ?? 0)).catch(() => 0),
    InsightsService.getRecords().then((r) => r.data).catch(() => null),
    DashboardService.getUserSeriesStats().then((r) => r.data).catch(() => null),
    DashboardService.getUserIssueStats().then((r) => r.data).catch(() => null),
  ]);
  const date = records?.firsts?.first_purchase?.date;
  return {
    spent,
    symbol: getSymbolFromCurrency(useUserStore().getUser()?.preferred_currency ?? "") ?? "",
    issues: Number(issueStats?.collectedIssueCount ?? fallback.issues),
    series: Number(seriesStats?.totalSeriesCount ?? fallback.series),
    since: date ? new Date(date).getFullYear() : null,
  };
}

/** A character whose picture stands on the shelf. */
export interface RoomCharacter {
  id: number;
  title: string;
  slug: string | null;
  series: number;
  image: string;
}

/** The characters in the most series, among those with a picture. */
export async function loadRoomCharacters(count = 2): Promise<RoomCharacter[]> {
  const page = await CharacterService.fetchCharacters(100, 0);
  const list: Entity[] = page?.data ?? [];
  return list
    .filter((c) => c.thumbnail)
    .sort((a, b) => (b.series_count ?? 0) - (a.series_count ?? 0))
    .slice(0, count)
    .map((c) => ({ id: c.id, title: c.title, slug: c.slug, series: c.series_count ?? 0, image: CharacterService.getCharacterImageById(c.id, c.last_updated) }));
}

/** An owned issue standing on the shelf. */
export interface RoomIssue {
  kind: "issue";
  id: number;
  number: number;
  title: string;
  issueTitle: string;
  seriesId: number;
  seriesTitle: string;
  publisher: string;
  slug: string;
  year: number | null;
  read: boolean;
  price: number | null;
  rgb: [number, number, number];
  cover: string;
}
export type RoomItem = RoomSeries | RoomIssue;

export const ROOM_MAX_ISSUES = 1500;
const ISSUE_PAGE = 500;

function toRoomIssue(i: LibraryIssue): RoomIssue {
  return {
    kind: "issue",
    id: i.id,
    number: i.number,
    title: `${i.series.title} #${i.number}`,
    issueTitle: i.title ?? "",
    seriesId: i.series.id,
    seriesTitle: i.series.title,
    publisher: "",
    slug: i.series.slug,
    year: i.cover_date ? new Date(i.cover_date).getFullYear() : null,
    read: !!i.is_read,
    price: i.bought_price ?? null,
    rgb: [70, 80, 110],
    cover: i.thumbnail ? IssueService.getIssueImageById(i.id, i.last_updated ?? undefined) : SeriesService.getSeriesImageById(i.series.id, i.series.last_updated ?? undefined),
  };
}

/** Every owned issue, up to the room's capacity; see shelfOrder for how they stand. */
export async function loadRoomIssues(): Promise<{ issues: RoomIssue[]; total: number }> {
  const first = await IssueService.fetchUserIssues(ISSUE_PAGE, 0);
  let list = first.issuesList;
  const total: number = first.pagination?.total ?? list.length;
  for (let offset = ISSUE_PAGE; offset < Math.min(total, ROOM_MAX_ISSUES); offset += ISSUE_PAGE) {
    const page = await IssueService.fetchUserIssues(ISSUE_PAGE, offset);
    list = list.concat(page.issuesList);
  }
  const owned = list.filter((i) => i.is_owned).map(toRoomIssue);
  return { issues: owned, total: owned.length };
}

/** Publisher together, then series together, then by number; a series the room does not know goes last. */
export function shelfOrder(issues: RoomIssue[], series: RoomSeries[]): RoomIssue[] {
  const publisher = new Map(series.map((s) => [s.id, s.publisher]));
  for (const i of issues) i.publisher = publisher.get(i.seriesId) ?? "";
  return issues.slice().sort((a, b) => (a.publisher || "\uffff").localeCompare(b.publisher || "\uffff") || a.seriesTitle.localeCompare(b.seriesTitle) || a.number - b.number);
}

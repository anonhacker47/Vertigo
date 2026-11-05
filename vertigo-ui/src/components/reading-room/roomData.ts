import SeriesService from "@/services/SeriesService";
import type { Series } from "@/types/series.types";

/** What the room needs to know about a series: enough for a cover, a spine colour and the card. */
export interface RoomSeries {
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

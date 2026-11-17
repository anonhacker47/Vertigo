export const SERIES_FILTER_KEYS = [
  "query", "genre", "creator", "character", "publisher", "series_format",
  "collection", "reading", "type", "min_rating",
] as const;

export type SeriesFilterKey = (typeof SERIES_FILTER_KEYS)[number];
export type SeriesFilterFields = Partial<Record<SeriesFilterKey, string>>;

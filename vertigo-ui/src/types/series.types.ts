import { MetronIdentifiable } from "./metron_identifiable.types";

export interface SeriesEntityRef {
  id: number;
  title: string;
  slug: string;
}

export interface SeriesNeighbour {
  id: number;
  slug: string;
  title?: string;
}

export interface SeriesNeighbours {
  previous: SeriesNeighbour | null;
  next: SeriesNeighbour | null;
}

export interface SlimSeries {
  id: number;
  title: string;
  slug: string;
  manga: number | null;
  thumbnail: string | null;
  last_updated: string | null;
}

export interface Series extends MetronIdentifiable {
  character: SeriesEntityRef[];
  description: string;
  dominant_color: [number, number, number];
  genre: string[];
  id: number;
  issue_count: number;
  notes: string;
  manga: boolean;
  owned_count: number;
  publisher: any;
  read_count: number;
  release_date: string;
  series_format: string;
  slug: string;
  team: string[];
  thumbnail: string;
  timestamp: string;
  last_updated?: string;
  title: string;
  url: string;
  user: {
    avatar_url: string;
    email: string;
    first_seen: string;
    id: number;
    series_url: string;
    url: string;
    username: string;
  };
  user_rating: number;
  creator: SeriesEntityRef[];
}

/** One option picked in the form's creator/character/genre comboboxes. */
export interface SeriesFormOption {
  id: number | string;
  value: string;
}

/**
 * Series fields as held by the add/edit forms: the thumbnail may be a freshly picked File, and the
 * entity lists are combobox options rather than the API's entity refs.
 */
export type SeriesFormData = Partial<Omit<Series, "thumbnail" | "creator" | "character" | "genre">> & {
  thumbnail?: string | File;
  creator?: SeriesFormOption[];
  character?: SeriesFormOption[];
  genre?: SeriesFormOption[];
};

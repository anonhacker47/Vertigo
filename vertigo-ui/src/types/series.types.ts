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
  thumbnail: string | File;
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
  metron_id?: number | null;
  metron_url?: string | null;
}

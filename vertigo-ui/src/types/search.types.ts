/** Rows from GET /search: just enough to list a hit and route to it. */
export interface SearchSeries {
  id: number;
  title: string;
  slug: string;
  series_format: string | null;
  manga: boolean;
  issue_count: number;
  owned_count: number;
  thumbnail: string | null;
}

export interface SearchIssue {
  id: number;
  number: number;
  title: string;
  is_owned: boolean;
  is_read: boolean;
  series: { id: number; title: string; slug: string; manga: boolean };
  thumbnail: string | null;
}

export interface SearchEntity {
  id: number;
  title: string;
  slug: string;
  thumbnail: string | null;
}

export interface SearchResponse {
  query: string;
  series: SearchSeries[];
  issues: SearchIssue[];
  publishers: SearchEntity[];
  creators: SearchEntity[];
  characters: SearchEntity[];
}

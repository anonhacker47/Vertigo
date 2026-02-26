export interface Entity {
  id: number;
  title: string;
  series_count: number;
  description: string | null;
  thumbnail: string | File;
  slug: string | null;
  timestamp: string;
  last_updated?: string;
  metron_id?: string
}
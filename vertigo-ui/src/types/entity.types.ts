export interface Entity {
  id: number;
  title: string;
  series_count:number;
  description: string | null;
  thumbnail: string | File;
  slug: string | null;
  timestamp: string; // ISO datetime string
}
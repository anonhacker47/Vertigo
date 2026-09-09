import { MetronIdentifiable } from "./metron_identifiable.types";
import { Series } from "./series.types";

export interface Issue extends MetronIdentifiable {
    id: number;
    title: string;
    number: number;
    description: string;
    slug: string;
    is_read: boolean;
    is_owned: boolean;
    bought_price: number | null;
    bought_date: Date | null;
    read_date: Date | null;
    timestamp: Date;
    series:Series;
    user_rating: number;
    notes: string;
    thumbnail: string | File;

}
  


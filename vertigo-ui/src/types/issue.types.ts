import { MetronIdentifiable } from "./metron_identifiable.types";
import { Series } from "./series.types";

export interface Issue extends MetronIdentifiable {
    id: number;
    title: string;
    number: number;
    description: string | null;
    cover_date: string | null;
    slug: string;
    is_read: boolean;
    is_owned: boolean;
    bought_price: number | null;
    bought_date: Date | null;
    read_date: Date | null;
    timestamp: Date;
    last_updated: string;
    series: Series;
    user_rating: number;
    notes: string;
    thumbnail: string | null;
}

/** The issue before/after another one in its series, by number. */
export interface IssueNeighbour {
    id: number;
    number: number;
    title: string;
}

export interface IssueNeighbours {
    previous: IssueNeighbour | null;
    next: IssueNeighbour | null;
    position: number;
    total: number;
}

export interface IssueEditFields {
    title: string;
    number: number | null;
    cover_date: string;
    description: string;
    notes: string;
    is_owned: boolean;
    bought_date: string;
    bought_price: number | null;
    is_read: boolean;
    read_date: string;
    metron_id: number | null;
    metron_url: string;
}

export interface IssueDraft {
    title: string;
    read: boolean;
    have: boolean;
    purchaseDate: string | null;
    readDate: string | null;
    price: number | null;
    metron_id: number | null;
    metron_url: string | null;
    cover: File | string | null;
}

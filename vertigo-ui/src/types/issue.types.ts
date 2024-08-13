export interface Issue {
    id: number;
    title: string;
    number: number;
    summary: string;
    slug: string;
    is_read: boolean;
    is_owned: boolean;
    bought_date: Date | null;
    read_date: Date | null;
    timestamp: Date;
}
  


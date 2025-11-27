export interface Series {
    character: string[];
    description: string;
    dominant_color: [number, number, number];
    genre: string[];
    id: number;
    issue_count: number;
    main_char_id: string | null;
    main_char_type: string | null;
    manga: number;
    owned_count: number;
    publisher: any;
    read_count: number;
    release_date: string; 
    series_format: string;
    slug: string;
    team: string[];
    thumbnail: string | File;
    timestamp: string; 
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
    creator: string[];
}

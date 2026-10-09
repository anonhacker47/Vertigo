export interface User {
  id: number;
  url: string;
  username: string;
  email: string;
  first_seen: string;
  series_url: string;
  profile_picture: string | null;
  preferred_currency: string | null;
}


export interface SeriesBasics {
  id: number;
  title: string;
  display_title: string;
  slug: string;
  series_format: string | null;
  manga: boolean;
  is_run: boolean;
  issue_count: number;
  owned_count: number;
  read_count: number;
  publisher: string | null;
  dominant_color: string | null;
  cover: string;
}

export interface IssueBasics {
  id: number;
  number: number;
  title: string;
  is_owned: boolean;
  is_read: boolean;
  bought_date: string | null;
  read_date: string | null;
  cover: string;
}

export type RunState = "read" | "owned" | "missing";

export interface RunTick {
  number: number;
  state: RunState;
}

export type UpNextTier = "1a" | "2a" | "1b" | "2b" | "3";

export interface UpNextEntry {
  tier: UpNextTier;
  finishes_run: boolean;
  reason: string;
  label: string;
  issue: IssueBasics;
  series: SeriesBasics;
}

export type UpNextHero = UpNextEntry;

export interface UpNextResponse {
  state: "ok" | "no_series" | "nothing_owned" | "nothing_unread";
  hero: UpNextHero | null;
  on_deck: UpNextEntry[];
  series_count?: number;
}

export type QueueMarker = "fresh" | "stalled" | "not_started" | null;

export interface ReadingQueueItem {
  series: SeriesBasics;
  next_issue: IssueBasics;
  tier: UpNextTier;
  unread_count: number;
  finishes_run: boolean;
  marker: QueueMarker;
  marker_date: string | null;
  last_read_at: string | null;
  run: RunTick[];
}

export interface ReadingQueueResponse {
  total_unread: number;
  series_count: number;
  items: ReadingQueueItem[];
}

export interface GetNextItem {
  series: SeriesBasics;
  missing_count: number;
  next_missing: number;
  caught_up: boolean;
  unread_on_shelf: number;
  last_bought: string | null;
  run: RunTick[];
}

export interface GetNextResponse {
  one_away: number;
  items: GetNextItem[];
  unstarted: { count: number; titles: string[] };
}

export type ActivityRange = "ytd" | "last_year" | "all";

export interface ActivityBucket {
  key: string;
  label: string;
  bought: number;
  read: number;
}

export interface DatedIssue {
  issue: IssueBasics;
  series: SeriesBasics;
}

export interface ActivityResponse {
  range: ActivityRange;
  mode: "month" | "year";
  buckets: ActivityBucket[];
  totals: { bought: number; read: number };
  figures: {
    unread: { count: number; series_count: number };
    last_read: (DatedIssue & { date: string; days: number }) | null;
    bought_to_read: { median_days: number; sample: number } | null;
    waiting_longest: (DatedIssue & { since: string; days: number }) | null;
  };
}

export interface RecordEvent extends DatedIssue {
  date: string;
}

export type CompletedStatus = "both" | "collected" | "read";

export interface CompletedRun {
  series: SeriesBasics;
  status: CompletedStatus;
  collected_at: string | null;
  read_at: string | null;
  completed_at: string;
}

export interface RecordsResponse {
  firsts: {
    first_read: RecordEvent | null;
    first_purchase: RecordEvent | null;
    on_vertigo_since: string | null;
  };
  records: {
    biggest_buying_month: { month: string; label: string; count: number } | null;
    biggest_reading_month: { month: string; label: string; count: number } | null;
    longest_complete_run: { series: SeriesBasics; issue_count: number } | null;
  };
  completed: CompletedRun[];
  single_volumes: { count: number; owned: number; read: number };
}

export interface FactLink {
  kind: "issue" | "series" | "creator" | "publisher" | "collection";
  id?: number;
  slug?: string;
  series_id?: number;
  number?: number;
}

export interface Fact {
  id: string;
  kicker: string;
  headline: string;
  detail: string;
  cover: string | null;
  swatches?: string[];
  link: FactLink | null;
}

export interface OnThisDayGroup {
  kind: "bought" | "read";
  year: number;
  date: string;
  count: number;
  items: { label: string; issue: IssueBasics; series: SeriesBasics }[];
}

export interface OnThisDay {
  scope: "day" | "week";
  groups: OnThisDayGroup[];
  anniversary: { years: number; since: string } | null;
}

export interface FactsResponse {
  on_this_day: OnThisDay | null;
  facts: Fact[];
}

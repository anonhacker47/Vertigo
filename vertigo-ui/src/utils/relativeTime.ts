const DAY_MS = 86_400_000;

function utcDay(value: Date | string): number {
  const d = typeof value === "string" ? new Date(value) : value;
  return Math.floor(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()) / DAY_MS);
}

export function daysSince(value: Date | string | null | undefined, from: Date = new Date()): number | null {
  if (!value) return null;
  return utcDay(from) - utcDay(value);
}

function unit(days: number): [number, string] {
  if (days < 14) return [days, "day"];
  if (days < 60) return [Math.max(2, Math.round(days / 7)), "week"];
  if (days < 365) return [Math.max(2, Math.round(days / 30.4)), "month"];
  if (days < 548) return [1, "year"];
  return [Math.max(2, Math.round(days / 365.25)), "year"];
}

export function relativeTime(days: number | null | undefined): string {
  if (days === null || days === undefined) return "";
  if (days === 0) return "today";
  if (days === 1) return "yesterday";
  if (days === -1) return "tomorrow";
  const future = days < 0;
  const [n, u] = unit(Math.abs(days));
  const phrase = u === "year" && n === 1 ? "a year" : `${n} ${u}${n === 1 ? "" : "s"}`;
  return future ? `in ${phrase}` : `${phrase} ago`;
}

export function spanText(days: number): string {
  const d = Math.abs(days);
  if (d < 14) return `${d} day${d === 1 ? "" : "s"}`;
  if (d < 60) return `${Math.max(2, Math.round(d / 7))} weeks`;
  if (d < 730) return `${Math.max(2, Math.round(d / 30.4))} months`;
  return `${Math.max(2, Math.round(d / 365.25))} years`;
}

export function capitalize(text: string): string {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : text;
}

export function formatDate(value: string | Date | null | undefined): string {
  if (!value) return "";
  return new Date(value).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

/** "Nov 2024" */
export function formatMonth(value: string | Date | null | undefined): string {
  if (!value) return "";
  return new Date(value).toLocaleDateString(undefined, { month: "short", year: "numeric" });
}

export function sinceText(value: string | null | undefined): string {
  const days = daysSince(value);
  if (days === null) return "";
  if (days >= 0 && days < 60) return relativeTime(days).replace(" ago", "");
  return formatMonth(value);
}

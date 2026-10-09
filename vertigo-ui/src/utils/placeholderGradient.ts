/**
 * Deterministic gradient for a title, used wherever a cover is missing so the same series
 * always gets the same placeholder (ImagePlaceHolderItem and the Insights cover tiles).
 */

export const PLACEHOLDER_PALETTE: ReadonlyArray<readonly [string, string]> = [
  ["#8B5CF6", "#06B6D4"], 
  ["#F43F5E", "#F59E0B"],
  ["#3B82F6", "#06B6D4"],
  ["#10B981", "#3B82F6"],
  ["#EC4899", "#8B5CF6"],
  ["#F97316", "#EF4444"],
  ["#14B8A6", "#0EA5E9"],
];

export function hashString(str: string): number {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = Math.trunc(Math.imul(31, h) + str.charCodeAt(i));
  }
  return Math.abs(h);
}

export function placeholderColors(title: string | null | undefined): readonly [string, string] {
  if (!title) return ["#444", "#222"];
  return PLACEHOLDER_PALETTE[hashString(title) % PLACEHOLDER_PALETTE.length];
}

export function placeholderGradient(title: string | null | undefined): string {
  const [a, b] = placeholderColors(title);
  return `linear-gradient(135deg, ${a}, ${b})`;
}

export function placeholderInitials(title: string | null | undefined): string {
  const words = String(title ?? "")
    .replace(/[^A-Za-z0-9 ]/g, " ")
    .split(/\s+/)
    .filter((w) => w && !/^(the|a|an|of|by|and|in)$/i.test(w));
  const initials = words.slice(0, 2).map((w) => w[0]).join("");
  return (initials || String(title ?? "").slice(0, 2)).toUpperCase();
}

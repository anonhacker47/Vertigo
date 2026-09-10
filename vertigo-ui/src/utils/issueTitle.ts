/**
 * Issues without a user-given title are auto-titled with their number (both the create
 * form and the backend do this), so a title only deserves showing when it says more than
 * the number does. These helpers keep every card that labels an issue consistent.
 */

const NUMERIC_TITLE = /^\d+(\.\d+)?$/;

/** True when the title carries information beyond the issue number. */
export function hasCustomIssueTitle(title: unknown, number: unknown): boolean {
  const text = String(title ?? "").trim();
  if (text === "") return false;
  if (number !== null && number !== undefined && number !== "") {
    return text !== String(number);
  }
  // No number available: a purely numeric title is the auto-generated one.
  return !NUMERIC_TITLE.test(text);
}

/** "#N" for the issue; falls back to the title when no number is available. */
export function issueNumberLabel(number: unknown, title?: unknown): string {
  if (number !== null && number !== undefined && number !== "") return `#${number}`;
  return `#${String(title ?? "").trim()}`;
}

/** One-line label: "#N" or "#N · Title" when the title is custom. */
export function issueDisplayLabel(title: unknown, number: unknown): string {
  const numberLabel = issueNumberLabel(number, title);
  return hasCustomIssueTitle(title, number)
    ? `${numberLabel} · ${String(title).trim()}`
    : numberLabel;
}

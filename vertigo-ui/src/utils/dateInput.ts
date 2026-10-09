/**
 * Bridges between the "YYYY-MM-DD" strings the forms keep (and send to the API) and the Date
 * objects PrimeVue's DatePicker works with. Both directions use the local calendar day, so a
 * date picked in the evening does not slip to the day before.
 */

export function ymdToDate(value: string | Date | null | undefined): Date | null {
  if (!value) return null;
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value;
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
  if (match) return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function dateToYmd(value: Date | null | undefined): string | null {
  if (!value || Number.isNaN(value.getTime())) return null;
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${value.getFullYear()}-${month}-${day}`;
}

/** Today as "YYYY-MM-DD" in the local calendar. */
export function todayYmd(): string {
  return dateToYmd(new Date()) as string;
}

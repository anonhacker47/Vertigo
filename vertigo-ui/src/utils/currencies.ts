import currencyCodes from "currency-codes";

export interface CurrencyOption {
  code: string;
  name: string;
}

export const currencyOptions: CurrencyOption[] = currencyCodes.data
  .map((c) => ({ code: c.code, name: c.currency }))
  .sort((a, b) => a.code.localeCompare(b.code));

const nameByCode = new Map(currencyOptions.map((c) => [c.code, c.name]));

export function currencyName(code: string | null | undefined): string {
  return (code && nameByCode.get(code)) || "";
}

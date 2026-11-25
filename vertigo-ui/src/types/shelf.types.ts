export type ShelfOrder = "publisher" | "series" | "newest" | "unread";
export type ShelfShow = "all" | "unread";
export type ShelfFinish = "charcoal" | "white";

/** How the 3D shelf is arranged; null standees or publisher mean automatic, or any. */
export interface ShelfSettings {
  standees: number[] | null;
  order: ShelfOrder;
  show: ShelfShow;
  publisher: number | null;
  finish: ShelfFinish;
}

export const SHELF_DEFAULTS: ShelfSettings = { standees: null, order: "publisher", show: "all", publisher: null, finish: "charcoal" };

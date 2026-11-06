export type ShelfOrder = "publisher" | "series" | "newest" | "unread";
export type ShelfShow = "all" | "unread";

/** How the 3D shelf is arranged; null standees or publisher mean automatic, or any. */
export interface ShelfSettings {
  standees: number[] | null;
  order: ShelfOrder;
  show: ShelfShow;
  publisher: number | null;
}

export const SHELF_DEFAULTS: ShelfSettings = { standees: null, order: "publisher", show: "unread", publisher: null };

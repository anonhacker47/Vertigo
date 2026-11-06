import Api from "@/services/Api";
import type { ShelfSettings } from "@/types/shelf.types";

export default {
  async getSettings(): Promise<ShelfSettings> {
    const response = await Api().get<ShelfSettings>("me/shelf");
    return response.data;
  },

  async saveSettings(settings: ShelfSettings): Promise<ShelfSettings> {
    const response = await Api().put<ShelfSettings>("me/shelf", settings);
    return response.data;
  },
};

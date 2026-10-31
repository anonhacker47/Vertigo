import Api from "@/services/Api";
import type { SearchResponse } from "@/types/search.types";

export default {
  async search(q: string, limit = 5): Promise<SearchResponse> {
    const { data } = await Api().get<SearchResponse>("search", { params: { q, limit } });
    return data;
  },
};

// services/JikanService.ts
import Api from "@/services/Api";

export default {
  getMangaByQuery(query: string) {
    return Api().get(`/jikan/manga/search`, {
      params: { query },
    });
  },

  getMangaDetail(mal_id: number) {
    return Api().get(`/jikan/manga/${mal_id}`);
  },

  getMangaEntities(mal_id: number) {
    return Api().get(`/jikan/manga/${mal_id}/entities`);
  },
};

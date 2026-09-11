import Api from "@/services/Api";

export default {
  getMangaByQuery(query: string) {
    return Api().get(`/tenrai/manga/search`, {
      params: { query },
    });
  },

  getMangaDetail(mal_id: number) {
    return Api().get(`/tenrai/manga/${mal_id}`);
  },

  getMangaEntities(mal_id: number) {
    return Api().get(`/tenrai/manga/${mal_id}/entities`);
  },
};

import Api from "@/services/Api";

export default {
  getSeriesByQuery(query: string) {
    return Api().get(`/metron/series/search`, {
      params: { query },
    });
  },

  getSeriesDetail(metron_id: number) {
    return Api().get(`/metron/series/${metron_id}`);
  },

  getSeriesEntities(metron_id: number) {
    return Api().get(`/metron/series/${metron_id}/entities`);
  },
};

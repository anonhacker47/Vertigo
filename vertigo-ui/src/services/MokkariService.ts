import Api from "@/services/Api";

export default {
  getSeriesbyQuery(query: string) {
    return Api().get(`/metron_search?query=${encodeURIComponent(query)}`);
  },

  getSeriesDetail(metron_id: number) {
    return Api().get(`/series_detail?series_id=${encodeURIComponent(metron_id)}`);
  },

  getSeriesEntities(metron_id: number) {
    return Api().get(`/series_entities?series_id=${encodeURIComponent(metron_id)}`);
  },
};
  
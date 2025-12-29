import Api from "@/services/Api";

export default {
    getSeriesbyQuery(query: string) {
        return Api().get(`/metron_search?query=${encodeURIComponent(query)}`);
    },

    getSeriesDetail(id: string) {
        return Api().get(`/series_detail?series_id=${encodeURIComponent(id)}`);
    },
};

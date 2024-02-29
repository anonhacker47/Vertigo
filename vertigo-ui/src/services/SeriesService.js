import Api from "src/services/Api";

export default {
  getSeries(token, id, orderby, orderdir) {
    return Api().get(
      `users/${id}/series?orderby=${orderby}&orderdir=${orderdir}`,
      token
    );
  },
  addSeries(data, headers) {
    return Api().post("series", data, headers);
  },
  removeSeries(data, headers) {
    return Api().delete(`series/${data}`, headers);
  },
  getSeriesbyId(id, headers) {
    return Api().get(`series/${id}`, headers);
  },
  getImagebyId(id) {
    return Api().defaults.baseURL + `/series/images/${id}`;
  },
  getSeriesKey(token) {
    return Api().get("series/key",
      token
    );
  },
};

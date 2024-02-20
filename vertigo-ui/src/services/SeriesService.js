import Api from "src/services/Api";

export default {
  getSeries(token, id, orderby, orderdir) {
    return Api().get(
      `users/${id}/series?orderby=${orderby}&orderdir=${orderdir}`,
      token
    );
  },
  addSeries(data) {
    return Api().post("series", data);
  },
  updateSeries(id,data){
    return Api().put(`series/${id}`,data)
  },
  removeSeries(data) {
    return Api().delete(`series/${data}`);
  },
  getSeriesbyId(id) {
    return Api().get(`series/${id}`);
  },
  getImagebyId(id) {
    return Api().defaults.baseURL + `/series/image/${id}`;
  },
  getSeriesKey() {
    return Api().get("series/key",
    );
  },
  getSeriesFieldValues(field){
    return Api().get(`/series/filter/${field}`);
  }
};

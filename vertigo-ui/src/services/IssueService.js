import Api from "@/services/Api";

export default {
  getIssues(token, id, orderby, orderdir) {
    return Api().get(
      `series/${id}/issues?orderby=${orderby}&orderdir=${orderdir}`,
      token
    );
  },
  addIssues(id, data) {
    return Api().post(`series/${id}/issues`, data);
  },
  getIssueCount(id) {
    return Api().get(`series/${id}/issue_count`);
  },
  updateIssue(id, data) {
    return Api().put(`series/issues/${id}/`, data);
  },
  // removeSeries(data, headers) {
  //   return Api().delete(`series/${data}`, headers);
  // },
  // getSeriesbyId(id, headers) {
  //   return Api().get(`series/${id}`, headers);
  // },
  // getImagebyId(id) {
  //   return Api().defaults.baseURL + `/series/images/${id}`;
  // },
};

import Api from "@/services/Api";

export default {
  getcards(token, orderby, orderdir) {
    return Api().get(`feed?orderby=${orderby}&orderdir=${orderdir}`, token);
  },
  addpost(data, headers) {
    return Api().post("series", data, headers);
  },
  removepost(data, headers) {
    return Api().delete(`series/${data}`, headers);
  },
  getcardbyid(id, headers) {
    return Api().get(`series/${id}`, headers);
  },
  getimagebyid(id) {
    return Api().defaults.baseURL + `/series/images/${id}`;
  },
};

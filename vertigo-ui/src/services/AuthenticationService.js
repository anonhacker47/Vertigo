import Api from "@/services/Api";

export default {
  register(credentials) {
    return Api().post("users", credentials);
  },
  login(credentials) {
    return Api().post("tokens",null,
      credentials);
  },
  refreshToken(data) {
    return Api().put("tokens",data);
  },
};
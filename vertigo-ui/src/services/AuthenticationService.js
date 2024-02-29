import Api from "src/services/Api";

export default {
  register(credentials) {
    return Api().post("users", credentials);
  },
  login(credentials) {
    return Api().post("tokens",null,
      credentials);
  },
  getUser(token){
    return Api().get("me",
      token);
  },
  refreshToken(data) {
    return Api().put("tokens",data);
  },
};
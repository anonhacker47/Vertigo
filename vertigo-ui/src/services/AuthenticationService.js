import Api from "@/services/Api";

export default {
  register(credentials) {
    return Api().post("users", credentials);
  },

  login(username,password) {
    const encoded_credentials = btoa(username + ":" + password);

    const headers = {
      Authorization: `Basic ${encoded_credentials}`,
    };

    return Api().post("tokens",null,
      {headers});
  },

  getUser(token){
    return Api().get("me",
      token);
  },
  refreshToken(data) {
    return Api().put("tokens",data);
  },
};
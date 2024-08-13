import Api from "@/services/Api";

export default {
  register(credentials: any) {
    return Api().post("users", credentials);
  },

  login(username: string,password: string) {
    const encoded_credentials = btoa(username + ":" + password);

    const headers = {
      Authorization: `Basic ${encoded_credentials}`,
    };

    return Api().post("tokens",null,
      {headers});
  },

  getUser(){
    return Api().get("me");
  },

  refreshToken(data: any) {
    return Api().put("tokens",data);
  },
};
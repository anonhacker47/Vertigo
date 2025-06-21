import Api from "@/services/Api";

export default {
  register(credentials: any) {
    return Api().post("users", credentials);
  },

  login(username: string, password: string) {
    const encoded_credentials = btoa(username + ":" + password);

    const headers = {
      Authorization: `Basic ${encoded_credentials}`,
    };

    return Api().post("tokens", null, { headers });
  },

  getUser() {
    return Api().get("me");
  },

  updateUser(data: any) {
    return Api().put("me", data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  async getUserPicture() {
    const response = await Api().get("me/profile-picture/", {
      responseType: "blob",
    });
    return URL.createObjectURL(response.data);
  },

  refreshToken(data: any) {
    return Api().put("tokens", data);
  },

  async exportCollection() {
    const response = await Api().get("export_data", {
      responseType: "blob", // ensure you receive a binary file
    });
    return response.data;
  },

  async deleteAllData() {
    return Api().delete("/delete_all_data");
  },
};

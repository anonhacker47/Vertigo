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

  async updateUser(data: any) {
    try {
      const response = await Api()
        .put("me", data, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
      return response;
    } catch (error) {
      const errorMessage = error.response?.data?.description ||
        error.response?.data?.message ||
        error.message ||
        "An unknown error occurred while updating user settings.";

      throw new Error(errorMessage);
    }
  },

  avatarUrl(user: { id: number; profile_picture: string | null; avatar?: string | null } | null | undefined) {
    if (!user) return null;
    return user.avatar ?? (user.profile_picture ? `${Api().defaults.baseURL}/users/${user.id}/avatar` : null);
  },

  revokeToken() {
    return Api().delete("tokens");
  },

  refreshToken(data: any) {
    return Api().put("tokens", data);
  },

  async deleteAllData() {
    return Api().delete("/delete_all_data");
  },
};

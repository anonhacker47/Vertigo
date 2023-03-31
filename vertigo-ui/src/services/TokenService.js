import { useUserStore } from "../store/user";

export default {
  getTokenHeader() {
    const token = localStorage.getItem("token");
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
    return headers;
  },
  getToken() {
    const token = localStorage.getItem("token");
    return token;
  },
  getUser() {
    const user = localStorage.getItem("userId");
    return user;
  },
};

import { defineStore } from "pinia";

// Define the state type
interface UserState {
  isUserLoggedIn: boolean;
  userId: string | null;
}

// Define the actions type
export const useUserStore = defineStore("user", {
  state: (): UserState => ({
    isUserLoggedIn: false,
    userId: null,
  }),
  actions: {
    addToken(token: string) {
      localStorage.setItem("token", token);
      localStorage.setItem("isUserLoggedIn", "true");
    },
    addUser(userId: string) {
      this.userId = userId;
      this.isUserLoggedIn = true; 
      localStorage.setItem("userId", userId);
    },
    getRefrehToken(token: string) {
      // This method is supposed to set the token in the state, but `token` is not in the state.
      // If you meant to update the `token`, you should add `token` to the state.
      localStorage.setItem("token", token);
    },
    getTokenHeader() {
      const token = localStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      };
      return headers;
    },
    getToken(): string | null {
      const token = localStorage.getItem("token");
      return token;
    },
    getUser(): string | null {
      const user = localStorage.getItem("userId");
      return user;
    },
    logout() {
      this.isUserLoggedIn = false;
      this.userId = null;
      localStorage.removeItem("token");
      localStorage.removeItem("isUserLoggedIn");
      localStorage.removeItem("userId");    },
  },
});

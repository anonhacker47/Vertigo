import { defineStore } from "pinia";
import type { User } from "@/types/user.types";

// Define the state type
interface UserState {
  isUserLoggedIn: boolean;
  user: User | null;
}

// Define the actions type
export const useUserStore = defineStore("user", {
  state: (): UserState => ({
    isUserLoggedIn: false,
    user: null,
  }),
  actions: {
    addToken(token: string) {
      localStorage.setItem("token", token);
      localStorage.setItem("isUserLoggedIn", "true");
    },
    addUser(user: User) {
      this.user = user;
      this.isUserLoggedIn = true; 
      localStorage.setItem("user", JSON.stringify(user));
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
    getUser(): User | null {
      const user = localStorage.getItem("user");
      return user ? (JSON.parse(user) as User) : null;
    },
    logout() {
      this.isUserLoggedIn = false;
      this.user = null;
      localStorage.removeItem("token");
      localStorage.removeItem("isUserLoggedIn");
      localStorage.removeItem("user");    },
  },
});

import { defineStore } from "pinia";

export const useUserStore = defineStore("user",{
    state: () => ({
            isUserLoggedIn:false,
    }),
    persist: true,
    actions: {
        addToken(token) {
            localStorage.setItem('token',token);
            this.isUserLoggedIn=true;
        },
        addUser(username) {
            this.username = username
        },
        getRefrehToken(token) {
            this.token = token
        },
    }
})
import { defineStore } from "pinia";

export const useUserStore = defineStore("user",{
    state: () => ({
        isUserLoggedIn:false,
        userId:null
    }),
    persist: true,
    actions: {
        addToken(token) {
            localStorage.setItem('token',token);
            localStorage.setItem('isUserLoggedIn',true)
            this.isUserLoggedIn = localStorage.getItem('isUserLoggedIn')
        },
        addUser(username) {
            this.username = username
        },
        getRefrehToken(token) {
            this.token = token
        },
    }
})
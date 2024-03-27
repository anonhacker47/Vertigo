import { defineStore } from "pinia";

export const useUserStore = defineStore("user",{
    state: () => ({
        isUserLoggedIn:false,
        userId:null,
    }),
    actions: {
        addToken(token) {
            localStorage.setItem('token',token);
            localStorage.setItem('isUserLoggedIn',true)
        },
        addUser(userId) {
            this.userId = userId
            localStorage.setItem('userId',userId);
            },
        getRefrehToken(token) {
            this.token = token
        },
    }
})
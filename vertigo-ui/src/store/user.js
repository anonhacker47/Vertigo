import { defineStore } from "pinia";

export const useUserStore = defineStore("user",{
    state: () => ({
        isUserLoggedIn:false,
        userId:null
    }),
    // persist: true,
    actions: {
        addToken(token) {
            localStorage.setItem('token',token);
            localStorage.setItem('isUserLoggedIn',true)
            
            this.isUserLoggedIn = localStorage.getItem('isUserLoggedIn')
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
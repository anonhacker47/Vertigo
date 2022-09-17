import { defineStore } from "pinia";

export const useUserStore = defineStore("user",{
    state: () => ({
            token : null,
            refreshtoken:null,
            username: null,
            isUserLoggedIn:false,
    }),
    persist: true,
    actions: {
        addToken(token,refreshtoken) {
            this.token = token
            this.refreshtoken = refreshtoken
        },
        addUser(username) {
            this.username = username
        },
        getRefrehToken(token) {
            this.token = token
        },
    }
})
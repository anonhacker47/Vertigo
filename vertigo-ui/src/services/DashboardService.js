import Api from "./Api";

export default {
    getUserSeriesStats(userId) {
        return Api().get(`users/${userId}/series/stats`);
    },

    getUserIssueStats(userId) {
        return Api().get(`users/${userId}/issues/stats`);
    },
    getUserFieldCount(userId, field, type) {
        return Api().get(`users/${userId}/${field}/${type}/count`);
    },
    getRecentPurchaseList(userId) {
        return Api().get(`users/${userId}/recent_purchases`);
    },
    getPurchasesPerMonth(userId) {
        return Api().get(`users/${userId}/purchases_per_month`);
    }
}
import Api from "./Api";

export default {
  getUserSeriesStats() {
    return Api().get(`users/series/stats`);
  },

  getUserIssueStats() {
    return Api().get(`users/issues/stats`);
  },
  getUserFieldCount(field, type, count) {
    return Api().get(`users/${field}/${type}/count?count=${count}`);
  },
  getRecentPurchaseList() {
    return Api().get(`users/recent_purchases`);
  },
  getPurchasesPerMonth(year: number) {
    return Api().get(`users/purchases_per_month`, {
      params: { year },
    });
  },
  getTotalSpent() {
    return Api().get(`users/total_spent`);
  },
};

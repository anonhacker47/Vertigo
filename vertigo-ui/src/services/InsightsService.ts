import Api from "./Api";
import type { ActivityRange, InsightsResponse, RecordsResponse } from "@/types/insights.types";

export default {
  getAll(range: ActivityRange = "ytd") {
    return Api().get<InsightsResponse>("insights", { params: { range } });
  },
  getRecords() {
    return Api().get<RecordsResponse>("insights/records");
  },
};

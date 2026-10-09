import Api from "./Api";
import type {
  ActivityRange,
  ActivityResponse,
  FactsResponse,
  GetNextResponse,
  ReadingQueueResponse,
  RecordsResponse,
  UpNextResponse,
} from "@/types/insights.types";

export default {
  getUpNext() {
    return Api().get<UpNextResponse>(`insights/up-next`);
  },
  getReadingQueue() {
    return Api().get<ReadingQueueResponse>(`insights/reading-queue`);
  },
  getGetNext() {
    return Api().get<GetNextResponse>(`insights/get-next`);
  },
  getActivity(range: ActivityRange = "ytd") {
    return Api().get<ActivityResponse>(`insights/activity`, { params: { range } });
  },
  getRecords() {
    return Api().get<RecordsResponse>(`insights/records`);
  },
  getFacts() {
    return Api().get<FactsResponse>(`insights/facts`);
  },
};

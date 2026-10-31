import Api from "@/services/Api";
import type { JobsResponse } from "@/types/jobs.types";

export default {
  async list(): Promise<JobsResponse> {
    const { data } = await Api().get<JobsResponse>("jobs");
    return data;
  },
};

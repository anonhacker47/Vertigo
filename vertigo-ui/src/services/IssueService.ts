import Api from "@/services/Api";
import { ApiResponse } from "@/types/api-response.types";
import { Issue } from "@/types/issue.types";

export default {
  async fetchIssues(
    id: Number,
    orderBy: string,
    orderDir: string
  ): Promise<Object> {
    const response = await Api().get<ApiResponse<Issue[]>>(
      `series/${id}/issues?orderBy=${orderBy}&orderDir=${orderDir}`
    );
    const issuesList = response.data.data;
    const pagination = response.data.pagination;
    return { issuesList, pagination };
  },

  addIssues(
    seriesId: any,
    issues: Array<{
      title: string;
      is_read: number;
      is_owned: number;
      bought_date?: string | null;
      read_date?: string | null;
      price?: number | null;
    }>
  ) {
    return Api().post(`series/${seriesId}/issues`, issues);
  },

  getIssueCount(id: number) {
    return Api().get(`series/${id}/issue_count`);
  },

  updateIssue(id: number, data: any) {
    return Api().put(`series/issues/${id}/`, data);
  },
  // removeSeries(data, headers) {
  //   return Api().delete(`series/${data}`, headers);
  // },
  // getSeriesbyId(id, headers) {
  //   return Api().get(`series/${id}`, headers);
  // },
  // getImagebyId(id) {
  //   return Api().defaults.baseURL + `/series/images/${id}`;
  // },
};

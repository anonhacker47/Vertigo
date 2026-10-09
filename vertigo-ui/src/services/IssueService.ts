import Api from "@/services/Api";
import { ApiResponse, Pagination } from "@/types/api-response.types";
import { Issue, IssueNeighbours, LibraryIssue, NewIssue } from "@/types/issue.types";

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

  async fetchUserIssues(
    limit: number,
    offset = 0
  ): Promise<{ issuesList: LibraryIssue[]; pagination: Pagination }> {
    const response = await Api().get<ApiResponse<LibraryIssue[]>>(
      `users/issues?limit=${limit}&offset=${offset}`
    );
    return { issuesList: response.data.data, pagination: response.data.pagination };
  },

  addIssues(seriesId: number, issues: NewIssue[]) {
    return Api().post<Issue[]>(`series/${seriesId}/issues`, issues);
  },

  getIssueCount(id: number) {
    return Api().get(`series/${id}/issue_count`);
  },

  getIssue(seriesId: number, number: number) {
    return Api().get(`series/${seriesId}/issues/${number}/`);
  },

  getIssueNeighbours(seriesId: number, number: number) {
    return Api().get<IssueNeighbours>(`series/${seriesId}/issues/${number}/neighbors`);
  },

  updateIssue(id: number, data: any) {
    return Api().put(`series/issues/${id}/`, data);
  },

  removeIssue(id: number) {
    return Api().delete(`series/issues/${id}/`);
  },

  createIssue(seriesId: number, data: NewIssue) {
    return Api().post<Issue>(`series/${seriesId}/single_issue`, data);
  },

  getIssueImageById(id: Issue["id"], lastUpdated?: string | Date) {
    if (lastUpdated) {
      const timestamp = new Date(lastUpdated).getTime();
      return Api().defaults.baseURL + `/series/issues/${id}/image?t=${timestamp}`;
    }
    return Api().defaults.baseURL + `/series/issues/${id}/image`;
  },

  updateIssueCover(
    id: number,
    source: File | string,
    opts: { background?: boolean } = {}
  ) {
    const formData = new FormData();
    formData.append("thumbnail", source);
    if (opts.background) formData.append("background", "true");

    return Api().put<Issue>(`series/issues/${id}/cover`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  removeIssueCover(id: number) {
    return Api().delete<void>(`series/issues/${id}/cover`);
  },
};

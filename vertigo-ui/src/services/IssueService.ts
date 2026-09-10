import Api from "@/services/Api";
import { ApiResponse } from "@/types/api-response.types";
import { Issue, IssueNeighbours } from "@/types/issue.types";

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
    return Api().post<Issue[]>(`series/${seriesId}/issues`, issues);
  },

  getIssueCount(id: number) {
    return Api().get(`series/${id}/issue_count`);
  },

  getIssue(seriesId: number, number: number) {
    return Api().get(`series/${seriesId}/issues/${number}/`);
  },

  /** Previous/next issue of the series by number, plus this issue's position in the run. */
  getIssueNeighbours(seriesId: number, number: number) {
    return Api().get<IssueNeighbours>(`series/${seriesId}/issues/${number}/neighbors`);
  },

  updateIssue(id: number, data: any) {
    return Api().put(`series/issues/${id}/`, data);
  },

  removeIssue(id: number) {
    return Api().delete(`series/issues/${id}/`);
  },

  createIssue(seriesId: number) {
    return Api().post(`series/${seriesId}/single_issue`);
  },

  /** URL of the issue's own cover, cache-busted by `lastUpdated` when given. */
  getIssueImageById(id: Issue["id"], lastUpdated?: string | Date) {
    if (lastUpdated) {
      const timestamp = new Date(lastUpdated).getTime();
      return Api().defaults.baseURL + `/series/issues/${id}/image?t=${timestamp}`;
    }
    return Api().defaults.baseURL + `/series/issues/${id}/image`;
  },

  /**
   * Set an issue's own cover. `source` is a File (saved inline), an http(s) URL, or the
   * string "noimage" to clear. With `background: true` (URLs only) the server queues the
   * download and replies 202 right away instead of downloading inline.
   */
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

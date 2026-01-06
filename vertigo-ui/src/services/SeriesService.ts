import Api from "@/services/Api";
import { Series } from "@/types/series.types";
import { ApiResponse } from "@/types/api-response.types";
import { SeriesFilterFields } from "@/types/series-filter.types";

export default {
  
  async fetchSeries(
    orderBy: string,
    orderDir: string,
    limit: number,
    offset = 0,
    filters: SeriesFilterFields = {}
  ): Promise<{ seriesList: Series[]; pagination: any }> {
    // Build query params
    const params = new URLSearchParams({
      orderBy,
      orderDir,
      limit: limit.toString(),
      offset: offset.toString(),
    });

    if (filters.query) params.append("query", filters.query);
    if (filters.creator) params.append("creator", filters.creator);
    if (filters.character) params.append("character", filters.character);
    if (filters.genre) params.append("genre", filters.genre);
    if (filters.publisher) params.append("publisher", filters.publisher);
    if (filters.series_format)
      params.append("series_format", filters.series_format);

    const response = await Api().get<ApiResponse<Series[]>>(
      `users/series?${params.toString()}`
    );

    return {
      seriesList: response.data.data,
      pagination: response.data.pagination,
    };
  },

  async addSeries(data: any) {
    const response = await Api().post("series", data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  updateSeries(id: any, data: any) {
    return Api().put(`series/${id}`, data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  async removeSeries(id: number): Promise<void> {
    await Api().delete<void>(`series/${id}`);
  },

  async getSeriesbyId(id: number): Promise<Series> {
    const response = await Api().get<Series>(`series/${id}`);
    return response.data;
  },

  getSeriesImageById(id: Series["id"]) {
    return Api().defaults.baseURL + `/series/image/${id}`;
  },

  getSeriesKey() {
    return Api().get("series/key");
  },

  getSeriesFieldValues(field: string) {
    return Api().get(`series/filter/${field}`);
  },

  getSeriesThumbBg() {
    return Api().defaults.baseURL +`/series/thumbnail/bg`;
  },

  getSeriesNeighbours(id: number) {
    return Api().get(`/series/${id}/neighbors`);
  },
};

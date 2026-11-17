import Api from "@/services/Api";
import type { Series } from "@/types/series.types";
import { ApiResponse } from "@/types/api-response.types";
import { SERIES_FILTER_KEYS, type SeriesFilterFields } from "@/types/series-filter.types";

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

    for (const key of SERIES_FILTER_KEYS) {
      const value = filters[key];
      if (value) params.append(key, value);
    }

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

  getSeriesImageById(id: Series["id"], lastUpdated?: string | Date) {
    if (lastUpdated) {
      const timestamp = new Date(lastUpdated).getTime();
      return Api().defaults.baseURL + `/series/image/${id}?t=${timestamp}`;
    }
    return Api().defaults.baseURL + `/series/image/${id}`;
  },

  getSeriesKey() {
    return Api().get("series/key");
  },

  getSeriesFilterValues() {
    return Api().get("series/filters");
  },

  getSeriesThumbBg() {
    return Api().defaults.baseURL + `/series/thumbnail/bg`;
  },

  getSeriesNeighbours(id: number) {
    return Api().get(`/series/${id}/neighbors`);
  },
};

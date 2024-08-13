import Api from "@/services/Api";
import { Series } from '@/types/series.types';
import { ApiResponse } from '@/types/api-response.types';

export default {
  async fetchSeries(userId: string, orderby: string, orderdir: string): Promise<Object> {
    const response = await Api().get<ApiResponse<Series[]>>(
      `users/${userId}/series?orderby=${orderby}&orderdir=${orderdir}`
    );
    const seriesList = response.data.data;
    const pagination = response.data.pagination;
    return {seriesList, pagination};
  },

  async addSeries(data: Partial<Series>): Promise<Series> {
    const response = await Api().post<Series>("series", data);
    return response.data;
  },


  updateSeries(id: any, data: any) {
    return Api().put(`series/${id}`, data)
  },

  async removeSeries(id: number): Promise<void> {
    await Api().delete<void>(`series/${id}`);
  },

  async getSeriesbyId(id: number): Promise<Series> {
    const response = await Api().get<Series>(`series/${id}`);
    return response.data;
  },

  getImagebyId(id: Series["id"]) {
    return Api().defaults.baseURL + `/series/image/${id}`;
  },
  
  getSeriesKey() {
    return Api().get("series/key",
    );
  },
  
  getSeriesFieldValues(field: string) {
    return Api().get(`series/filter/${field}`);
  },

  getSeriesThumbBg() {
    return Api().get(`/series/thumbnail/bg`);
  }
};

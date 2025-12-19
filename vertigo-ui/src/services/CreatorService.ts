import Api from "@/services/Api";
import { Entity } from "@/types/entity.types";

export default {
  async fetchCreators(limit = 28, offset = 0, query = "") {
    const params: any = { limit, offset };
    if (query) params.query = query;
    const response = await Api().get("/creator", { params });
    return response.data;
  },

  async getCreatorById(id: number): Promise<Entity> {
    const response = await Api().get<Entity>(`creator/${id}`);
    return response.data;
  },

  getCreatorNeighbours(id: number) {
    return Api().get(`/creator/${id}/neighbours`);
  },

  async createCreator(data: any) {
    const response = await Api().post("creator", data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  async updateCreator(id: Entity["id"], data: Entity) {
    const response = await Api().patch(`creator/${id}`, data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  getCreatorImageById(id: Entity["id"]) {
    return Api().defaults.baseURL + `/creator/image/${id}`;
  },

  async deleteCreator(id: number) {
    await Api().delete(`creator/${id}`);
  },

};

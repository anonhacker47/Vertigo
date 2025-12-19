import Api from "@/services/Api";
import { Entity } from "@/types/entity.types";

export default {
  async fetchPublishers(limit = 28, offset = 0, query = "") {
    const params: any = { limit, offset };
    if (query) params.query = query;
    const response = await Api().get("publisher", { params });
    return response.data;
  },

  async getPublisherById(id: number): Promise<Entity> {
    const response = await Api().get<Entity>(`publisher/${id}`);
    return response.data;
  },

  getPublisherNeighbours(id: number) {
    return Api().get(`/publisher/${id}/neighbours`);
  },

  async createPublisher(data: any) {
    const response = await Api().post("publisher", data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  async updatePublisher(id, data: any) {
    const response = await Api().patch(`publisher/${id}`, data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  getPublisherImageById(id: Entity["id"]) {
    return Api().defaults.baseURL + `/publisher/image/${id}`;
  },

  async deletePublisher(id: number) {
    await Api().delete(`publisher/${id}`);
  },

};

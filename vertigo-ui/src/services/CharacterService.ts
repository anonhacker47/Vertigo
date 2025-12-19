import Api from "@/services/Api";
import { Entity } from "@/types/entity.types";

export default {
  async fetchCharacters(limit = 28, offset = 0, query = "") {
    const params: any = { limit, offset };
    if (query) params.query = query;
    const response = await Api().get("/character", { params });
    return response.data;
  },

  async getCharacterById(id: number): Promise<Entity> {
    const response = await Api().get<Entity>(`character/${id}`);
    return response.data;
  },

  getCharacterNeighbours(id: number) {
    return Api().get(`/character/${id}/neighbours`);
  },

  async createCharacter(data: any) {
    const response = await Api().post("character", data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  async updateCharacter(id: Entity["id"], data: Entity) {
    const response = await Api().patch(`character/${id}`, data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  getCharacterImageById(id: Entity["id"]) {
    return Api().defaults.baseURL + `/character/image/${id}`;
  },

  async deleteCharacter(id: number) {
    await Api().delete(`character/${id}`);
  },
};

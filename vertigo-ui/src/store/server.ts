import { defineStore } from "pinia";
import Api from "@/services/Api";

export const useServerStore = defineStore("server", {
  state: () => ({ demo: false }),
  actions: {
    async load() {
      try {
        const { data } = await Api().get("ping");
        this.demo = !!data.demo;
      } catch {
        return;
      }
      document.documentElement.classList.toggle("demo", this.demo);
    },
  },
});

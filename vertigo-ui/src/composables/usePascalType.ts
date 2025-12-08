import { computed, Ref } from "vue";

export function usePascalType(type: string | Ref<string>) {
  return computed(() => {
    const val = typeof type === "string" ? type : type.value;
    return val.charAt(0).toUpperCase() + val.slice(1).toLowerCase();
  });
}
import { computed, onMounted, ref, type ComputedRef, type Ref } from "vue";
import InsightsService from "@/services/InsightsService";
import type { ActivityRange, InsightsResponse } from "@/types/insights.types";

export interface InsightsSection<T> {
  data: ComputedRef<T | null>;
  loading: Ref<boolean>;
  refreshing: Readonly<Ref<boolean>>;
  error: Ref<string | null>;
  reload: () => Promise<void>;
}

const page = ref<InsightsResponse | null>(null);
const loading = ref(false);
const refreshing = ref(false);
const rangeRefreshing = ref(false);
const error = ref<string | null>(null);
let range: ActivityRange = "ytd";
let inflight: Promise<void> | null = null;

export function loadInsights(nextRange?: ActivityRange): Promise<void> {
  if (nextRange) range = nextRange;
  if (inflight) return inflight;
  const flag = page.value === null ? loading : nextRange ? rangeRefreshing : refreshing;
  flag.value = true;
  error.value = null;
  inflight = InsightsService.getAll(range)
    .then((response) => { page.value = response.data; })
    .catch((e) => {
      console.error(e);
      error.value = "Couldn't load this. Try again.";
    })
    .finally(() => {
      flag.value = false;
      inflight = null;
    });
  return inflight;
}

export function useInsightsSection<K extends keyof InsightsResponse>(key: K): InsightsSection<InsightsResponse[K]> {
  onMounted(() => void loadInsights());
  return {
    data: computed(() => page.value?.[key] ?? null),
    loading,
    refreshing: key === "activity" ? computed(() => refreshing.value || rangeRefreshing.value) : refreshing,
    error,
    reload: () => loadInsights(),
  };
}

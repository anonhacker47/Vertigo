import { onMounted, ref, type Ref } from "vue";

export interface InsightsSection<T> {
  data: Ref<T | null>;
  loading: Ref<boolean>;
  refreshing: Ref<boolean>;
  error: Ref<string | null>;
  reload: () => Promise<void>;
}

export function useInsightsSection<T>(fetcher: () => Promise<{ data: T }>): InsightsSection<T> {
  const data = ref<T | null>(null) as Ref<T | null>;
  const loading = ref(false);
  const refreshing = ref(false);
  const error = ref<string | null>(null);

  async function reload() {
    if (data.value === null) loading.value = true;
    else refreshing.value = true;
    error.value = null;
    try {
      data.value = (await fetcher()).data;
    } catch (e) {
      console.error(e);
      error.value = "Couldn't load this. Try again.";
    } finally {
      loading.value = false;
      refreshing.value = false;
    }
  }

  onMounted(reload);

  return { data, loading, refreshing, error, reload };
}

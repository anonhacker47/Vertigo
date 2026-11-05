import { computed, onBeforeUnmount, ref } from "vue";
import TransferService from "@/services/TransferService";
import { refreshJobs } from "@/composables/useJobs";
import type { TransferRun } from "@/types/transfer.types";

const POLL_MS = 1000;

/** Polls one restore run until it finishes and nudges the header's job list on both ends. */
export function useTransferRun() {
  const run = ref<TransferRun | null>(null);
  let timer: ReturnType<typeof setTimeout> | null = null;

  const active = computed(() => run.value?.status === "queued" || run.value?.status === "running");
  const percent = computed(() => {
    const current = run.value;
    if (!current) return 0;
    if (current.status === "done") return 100;
    if (!current.total) return 0;
    return Math.min(100, Math.round((current.done / current.total) * 100));
  });

  function stop() {
    if (timer) clearTimeout(timer);
    timer = null;
  }

  async function poll() {
    stop();
    const current = run.value;
    if (!current || !active.value) return;
    try {
      run.value = await TransferService.getRun(current.id);
    } catch {
      run.value = {
        ...current,
        status: "failed",
        error: "Lost track of the job. Check your collection to see what arrived.",
      };
    }
    if (active.value) timer = setTimeout(poll, POLL_MS);
    else refreshJobs();
  }

  function track(initial: TransferRun) {
    stop();
    run.value = initial;
    refreshJobs();
    if (active.value) timer = setTimeout(poll, POLL_MS);
  }

  function reset() {
    stop();
    run.value = null;
  }

  onBeforeUnmount(stop);

  return { run, active, percent, track, reset };
}

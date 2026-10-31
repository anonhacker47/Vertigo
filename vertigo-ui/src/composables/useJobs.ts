import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import router from "@/router";
import JobsService from "@/services/JobsService";
import type { Job } from "@/types/jobs.types";

/**
 * Shared list of pending background jobs. Polled every few seconds only while something is
 * pending; otherwise refreshed on navigation and when a flow that queues work asks for it.
 */
const POLL_MS = 3000;

const jobs = ref<Job[]>([]);
const running = computed(() => jobs.value.filter((j) => j.status === "running").length);
const queued = computed(() => jobs.value.length - running.value);

let subscribers = 0;
let timer: ReturnType<typeof setTimeout> | null = null;
let inFlight: Promise<void> | null = null;

function refresh(): Promise<void> {
  if (inFlight) return inFlight;
  inFlight = JobsService.list()
    .then((data) => {
      jobs.value = data.jobs;
    })
    .catch((e) => console.error("Jobs refresh failed:", e))
    .finally(() => {
      inFlight = null;
    });
  return inFlight;
}

function schedule() {
  if (timer) clearTimeout(timer);
  timer = null;
  if (!subscribers || !jobs.value.length) return;
  timer = setTimeout(async () => {
    if (!document.hidden) await refresh();
    schedule();
  }, POLL_MS);
}

function refreshJobs() {
  if (subscribers) void refresh().then(schedule);
}

router.afterEach(() => refreshJobs());
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) refreshJobs();
});

function useJobs() {
  onMounted(() => {
    subscribers += 1;
    if (subscribers === 1) refreshJobs();
  });
  onBeforeUnmount(() => {
    subscribers -= 1;
    if (!subscribers && timer) {
      clearTimeout(timer);
      timer = null;
    }
  });
  return { jobs, running, queued };
}

export { useJobs, refreshJobs };

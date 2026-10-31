export type JobStatus = "queued" | "running";

export interface Job {
  id: string;
  kind: string;
  label: string;
  queue: string;
  status: JobStatus;
  queued_at: string;
  started_at: string | null;
}

export interface JobsResponse {
  jobs: Job[];
}

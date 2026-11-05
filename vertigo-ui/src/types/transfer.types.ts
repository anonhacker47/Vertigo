export type RunStatus = "queued" | "running" | "done" | "failed";
export type RunKind = "restore";

/** A restore running on the server; polled at GET /transfer/runs/<id>. */
export interface TransferRun {
  id: string;
  kind: RunKind;
  label: string;
  status: RunStatus;
  total: number;
  done: number;
  /** Counts, plus `safety_backup` (a file name) when a replace saved the old collection. */
  summary: Record<string, number | string>;
  error: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export type RestoreMode = "merge" | "replace";

export interface BackupInfo {
  version: number;
  created_at: string | null;
  username: string | null;
  series: number;
  issues: number;
  entities: number;
}

export interface RestoreConflict {
  error: "account_not_empty";
  message: string;
  backup: BackupInfo;
  account: { series: number; issues: number; entities: number };
}

import Api from "@/services/Api";
import type { RestoreMode, TransferRun } from "@/types/transfer.types";

const MULTIPART = { headers: { "Content-Type": "multipart/form-data" } };

function upload(file: File, extra: Record<string, string | undefined> = {}): FormData {
  const data = new FormData();
  data.append("file", file, file.name);
  for (const [key, value] of Object.entries(extra)) {
    if (value !== undefined && value !== "") data.append(key, value);
  }
  return data;
}

/** The server's own words for a failed transfer call, or the fallback. */
export function transferErrorMessage(error: unknown, fallback: string): string {
  const data = (error as { response?: { data?: { description?: string; message?: string } } })?.response?.data;
  return data?.description || data?.message || fallback;
}

export default {
  async exportSpreadsheet(): Promise<Blob> {
    const { data } = await Api().get<Blob>("export_data", { responseType: "blob" });
    return data;
  },

  async downloadBackup(): Promise<Blob> {
    const { data } = await Api().get<Blob>("backup", { responseType: "blob" });
    return data;
  },

  /** 202 with the run; a 409 (account not empty, no mode) rejects with a RestoreConflict body. */
  async restore(file: File, mode?: RestoreMode): Promise<TransferRun> {
    const { data } = await Api().post<TransferRun>("restore", upload(file, { mode }), MULTIPART);
    return data;
  },

  async getRun(id: string): Promise<TransferRun> {
    const { data } = await Api().get<TransferRun>(`transfer/runs/${id}`);
    return data;
  },
};

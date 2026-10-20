import Api from "@/services/Api";
import type { IntegrationsStatus, MetronTestResult } from "@/types/integrations.types";

export function integrationErrorMessage(error: any, fallback: string): string {
  const data = error?.response?.data;
  if (data?.error === "rate_limited") {
    const wait = data.retry_after ? ` Try again in ${data.retry_after}s.` : " Try again in a minute.";
    return "Metron is rate limiting requests." + wait;
  }
  return (data?.error ? data.message : data?.description) || fallback;
}

export default {
  getStatus() {
    return Api().get<IntegrationsStatus>("/integrations");
  },

  saveMetronToken(api_token: string) {
    return Api().put<IntegrationsStatus>("/integrations/metron", { api_token });
  },

  clearMetronToken() {
    return Api().delete<IntegrationsStatus>("/integrations/metron");
  },

  testMetron() {
    return Api().post<MetronTestResult>("/integrations/metron/test");
  },
};

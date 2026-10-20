export interface RateLimitWindow {
  limit: number | null;
  remaining: number | null;
  reset: string | null;
}

export interface MetronRateLimit {
  burst: RateLimitWindow;
  sustained: RateLimitWindow;
}

export type MetronTokenSource = "user" | "server" | null;

export interface MetronStatus {
  configured: boolean;
  source: MetronTokenSource;
  /** Masked tail of the user's own token; null for the server token. */
  token_hint: string | null;
  server_token: boolean;
  rate_limit: MetronRateLimit | null;
}

export interface MyAnimeListStatus {
  configured: boolean;
  source: "server";
}

export interface IntegrationsStatus {
  metron: MetronStatus;
  myanimelist: MyAnimeListStatus;
}

export interface MetronTestResult {
  ok: boolean;
  source: MetronTokenSource;
  rate_limit: MetronRateLimit | null;
}

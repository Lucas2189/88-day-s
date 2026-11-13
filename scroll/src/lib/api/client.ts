import type { ApiError, ContentItem, FeedResponse } from "@/lib/content/types";
import type { SearchResponse } from "@/app/api/search/route";

export class ApiClientError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: ApiError,
  ) {
    super(body.error);
    this.name = "ApiClientError";
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (res.ok) return (await res.json()) as T;
  let body: ApiError = { error: `Request failed (${res.status})`, code: "provider_error" };
  try {
    body = (await res.json()) as ApiError;
  } catch {
    /* keep default */
  }
  throw new ApiClientError(res.status, body);
}

export const api = {
  feed: (params: { providers?: string[]; categories?: string[] } = {}) => {
    const q = new URLSearchParams();
    if (params.providers?.length) q.set("providers", params.providers.join(","));
    if (params.categories?.length) q.set("categories", params.categories.join(","));
    return fetch(`/api/feed?${q.toString()}`).then((r) => handle<FeedResponse>(r));
  },
  resolve: (url: string, categories?: string[]) =>
    fetch("/api/resolve", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ url, categories }),
    }).then((r) => handle<{ item: ContentItem }>(r)),
  search: (q: string) => fetch(`/api/search?q=${encodeURIComponent(q)}`).then((r) => handle<SearchResponse>(r)),
};

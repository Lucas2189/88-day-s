import type { ContentItem, ProviderId, ProviderInfo, CategoryId } from "@/lib/content/types";

export interface ResolveContext {
  /** Optional category hints supplied by the submitting user. */
  categories?: CategoryId[];
  origin?: ContentItem["origin"];
}

export interface SearchOptions {
  query: string;
  limit?: number;
}

export interface FeedOptions {
  limit?: number;
  categories?: CategoryId[];
}

export class ProviderError extends Error {
  constructor(
    public readonly provider: ProviderId,
    public readonly code: "not_found" | "provider_error" | "unsupported" | "rate_limited",
    message: string,
  ) {
    super(message);
    this.name = "ProviderError";
  }
}

/**
 * Every integration implements this interface. Adapters must only use
 * officially supported endpoints (oEmbed, public APIs with credentials).
 */
export interface ProviderAdapter {
  readonly info: ProviderInfo;
  /** Resolve a canonical public URL into a ContentItem using authorized endpoints. */
  resolve(externalId: string, canonicalUrl: string, ctx?: ResolveContext): Promise<ContentItem>;
  /** Optional: fetch discovery content when the provider API allows it. */
  feed?(opts: FeedOptions): Promise<ContentItem[]>;
  /** Optional: search the provider catalog when the provider API allows it. */
  search?(opts: SearchOptions): Promise<ContentItem[]>;
}

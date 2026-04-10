/**
 * Server-side CMS data fetcher.
 * Used by Next.js Server Components (marketing pages) to load content from the FastAPI CMS endpoints.
 * ISR caching: pages rebuild from DB every 60 seconds.
 */

import type {
  BlogPostDetail,
  BlogPostSummary,
  CalculatorFormula,
  CmsPageResponse,
} from "./cmsTypes";
import { fetchWithTimeout } from "./server-fetch";
import { getApiBaseUrl } from "./runtime-config";

const API_BASE = getApiBaseUrl();
const CMS_FETCH_TIMEOUT_MS = 2500;

async function serverFetch<T>(path: string): Promise<T | null> {
  try {
    const res = await fetchWithTimeout(
      `${API_BASE}/api/v1${path}`,
      {
        next: { revalidate: 60 }, // ISR — refresh every 60s
        headers: {
          accept: "application/json",
          "content-type": "application/json",
        },
      },
      CMS_FETCH_TIMEOUT_MS,
    );
    if (!res.ok) return null;
    return res.json() as Promise<T>;
  } catch {
    return null;
  }
}

export async function getCmsPage(slug: string) {
  return serverFetch<CmsPageResponse>(`/cms/pages/${slug}`);
}

export async function getFeaturedPosts() {
  return serverFetch<BlogPostSummary[]>("/cms/blog/featured");
}

export async function getPublishedPosts(category?: string) {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  return serverFetch<BlogPostSummary[]>(`/cms/blog${query}`);
}

export async function getBlogPost(slugOrId: string) {
  return serverFetch<BlogPostDetail>(`/cms/blog/${slugOrId}`);
}

export async function getActiveFormula() {
  return serverFetch<CalculatorFormula>("/cms/calculator/active");
}

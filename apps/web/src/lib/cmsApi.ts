const rawApiBase = (process.env.NEXT_PUBLIC_API_URL ?? "/api/bio").replace(/\/$/, "");
const API =
  rawApiBase.startsWith("http") && !rawApiBase.endsWith("/api/v1")
    ? `${rawApiBase}/api/v1`
    : rawApiBase;

import type {
  BlogPostDetail,
  BlogPostSummary,
  CalculatorFormula,
  CmsPageResponse,
  MediaAsset,
} from "./cmsTypes";

const CMS_FETCH_TIMEOUT_MS = 3500;

async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), CMS_FETCH_TIMEOUT_MS);
  let res: Response;

  try {
    res = await fetch(`${API}${path}`, {
      ...opts,
      credentials: "include",
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...(opts?.headers ?? {}) },
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error("The CMS request timed out. Please retry after the API is healthy.");
    }

    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }

  if (!res.ok) {
    const bodyText = await res.text();
    let message = bodyText || `HTTP ${res.status}`;
    if (bodyText) {
      try {
        const body = JSON.parse(bodyText) as {
          error?: { message?: string };
          detail?: string;
          message?: string;
        };
        message = body.error?.message ?? body.detail ?? body.message ?? message;
      } catch {
        message = bodyText;
      }
    }
    throw new Error(message);
  }
  if (res.status === 204) return null as T;
  return res.json() as Promise<T>;
}

export const cmsApi = {
  getPage: <TSections extends Record<string, unknown> = Record<string, unknown>>(slug: string) =>
    apiFetch<CmsPageResponse<TSections>>(`/cms/pages/${slug}`),
  updatePage: (slug: string, data: Record<string, string>) =>
    apiFetch(`/cms/pages/${slug}`, { method: "PATCH", body: JSON.stringify(data) }),
  updateSection: (pageSlug: string, sectionKey: string, content: unknown) =>
    apiFetch(`/cms/sections/${pageSlug}/${sectionKey}`, {
      method: "PATCH",
      body: JSON.stringify({ content_json: content }),
    }),
  listPosts: (all = true) => apiFetch<BlogPostSummary[]>(all ? "/cms/blog/all" : "/cms/blog"),
  getPost: (id: string) => apiFetch<BlogPostDetail>(`/cms/blog/id/${id}`),
  createPost: (data: Record<string, unknown>) =>
    apiFetch<BlogPostDetail>("/cms/blog", { method: "POST", body: JSON.stringify(data) }),
  updatePost: (id: string, data: Record<string, unknown>) =>
    apiFetch<BlogPostDetail>(`/cms/blog/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deletePost: (id: string) => apiFetch(`/cms/blog/${id}`, { method: "DELETE" }),
  getActiveFormula: () => apiFetch<CalculatorFormula>("/cms/calculator/active"),
  listFormulas: () => apiFetch<CalculatorFormula[]>("/cms/calculator"),
  createFormula: (data: Record<string, unknown>) =>
    apiFetch("/cms/calculator", { method: "POST", body: JSON.stringify(data) }),
  updateFormula: (id: string, data: Record<string, unknown>) =>
    apiFetch(`/cms/calculator/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  activateFormula: (id: string) => apiFetch(`/cms/calculator/${id}/activate`, { method: "PATCH" }),
  listMedia: () => apiFetch<MediaAsset[]>("/cms/media"),
  createMedia: (data: Record<string, unknown>) =>
    apiFetch<MediaAsset>("/cms/media", { method: "POST", body: JSON.stringify(data) }),
  deleteMedia: (id: string) => apiFetch(`/cms/media/${id}`, { method: "DELETE" }),
};

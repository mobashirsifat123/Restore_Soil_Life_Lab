import type { AdminUserListResponse, UserActivityLogListResponse } from "./adminTypes";

const API = "/api/bio";
const ADMIN_FETCH_TIMEOUT_MS = 3500;

async function adminFetch<T>(path: string): Promise<T> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), ADMIN_FETCH_TIMEOUT_MS);
  let response: Response;

  try {
    response = await fetch(`${API}${path}`, {
      credentials: "include",
      cache: "no-store",
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error("The admin request timed out. Check the API or database connection.");
    }

    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }

  if (!response.ok) {
    const bodyText = await response.text();
    try {
      const body = JSON.parse(bodyText) as { error?: { message?: string }; detail?: string };
      throw new Error(
        (body.error?.message ?? body.detail ?? bodyText) || `HTTP ${response.status}`,
      );
    } catch {
      throw new Error(bodyText || `HTTP ${response.status}`);
    }
  }

  return response.json() as Promise<T>;
}

export const adminApi = {
  listUsers: () => adminFetch<AdminUserListResponse>("/admin/users"),
  listUserLog: () => adminFetch<UserActivityLogListResponse>("/admin/user-log"),
};

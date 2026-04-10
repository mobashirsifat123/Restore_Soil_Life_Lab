import type { AuthSessionListResponse, MemberProfile } from "@bio/api-client";
import { cookies } from "next/headers";
import { fetchWithTimeout } from "./server-fetch";
import { getApiBaseUrl } from "./runtime-config";

const apiBaseUrl = getApiBaseUrl();
const SERVER_AUTH_FETCH_TIMEOUT_MS = 1800;

async function fetchServerAuthResource<T>(path: string): Promise<T | null> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();

  if (!cookieHeader) {
    return null;
  }

  let response: Response;
  try {
    response = await fetchWithTimeout(
      `${apiBaseUrl}/api/v1${path}`,
      {
        cache: "no-store",
        headers: {
          accept: "application/json",
          cookie: cookieHeader,
        },
      },
      SERVER_AUTH_FETCH_TIMEOUT_MS,
    );
  } catch {
    return null;
  }

  if (!response.ok) {
    return null;
  }

  return response.json() as Promise<T>;
}

export async function getServerProfile(): Promise<MemberProfile | null> {
  return fetchServerAuthResource<MemberProfile>("/auth/profile");
}

export async function getServerAuthSessions(): Promise<AuthSessionListResponse | null> {
  return fetchServerAuthResource<AuthSessionListResponse>("/auth/sessions");
}

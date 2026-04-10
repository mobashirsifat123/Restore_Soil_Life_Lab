import type { SessionResponse } from "@bio/api-client";
import { cookies } from "next/headers";
import { fetchWithTimeout } from "./server-fetch";
import { getApiBaseUrl } from "./runtime-config";

const apiBaseUrl = getApiBaseUrl();
const SESSION_FETCH_TIMEOUT_MS = 1800;

export async function getServerSession(): Promise<SessionResponse | null> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();

  if (!cookieHeader) {
    return null;
  }

  let response: Response;
  try {
    response = await fetchWithTimeout(
      `${apiBaseUrl}/api/v1/auth/session`,
      {
        cache: "no-store",
        headers: {
          accept: "application/json",
          cookie: cookieHeader,
        },
      },
      SESSION_FETCH_TIMEOUT_MS,
    );
  } catch {
    return null;
  }

  if (!response.ok) {
    return null;
  }

  return response.json() as Promise<SessionResponse>;
}

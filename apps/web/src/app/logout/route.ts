import { NextRequest, NextResponse } from "next/server";
import { fetchWithTimeout } from "@/lib/server-fetch";
import { getApiBaseUrl } from "@/lib/runtime-config";

const apiBaseUrl = getApiBaseUrl();
const sessionCookieName = process.env.AUTH_SESSION_COOKIE_NAME ?? "bio_session";

export async function GET(request: NextRequest) {
  const cookieHeader = request.headers.get("cookie");

  if (cookieHeader) {
    try {
      await fetchWithTimeout(
        `${apiBaseUrl}/api/v1/auth/logout`,
        {
          method: "POST",
          headers: {
            cookie: cookieHeader,
          },
          cache: "no-store",
        },
        3000,
      );
    } catch {
      // Best effort only: we still clear the browser cookie below.
    }
  }

  const redirectTo = request.nextUrl.searchParams.get("redirect") || "/";
  const response = NextResponse.redirect(new URL(redirectTo, request.url));
  response.cookies.set({
    name: sessionCookieName,
    value: "",
    maxAge: 0,
    expires: new Date(0),
    path: "/",
    httpOnly: true,
    sameSite: "lax",
  });

  return response;
}

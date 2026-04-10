import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { fetchWithTimeout } from "@/lib/server-fetch";
import { getApiBaseUrl } from "@/lib/runtime-config";

export const dynamic = "force-dynamic";

const apiBaseUrl = getApiBaseUrl();

function getProxyTimeoutMs(method: string, pathStr: string) {
  if (pathStr === "chat/widget-config" || pathStr === "auth/session") {
    return 2500;
  }

  if (method === "GET" || method === "HEAD") {
    return 5000;
  }

  if (pathStr.startsWith("chat/")) {
    return 12000;
  }

  return 8000;
}

function buildProxyHeaders(request: NextRequest): Headers {
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");
  return headers;
}

async function proxy(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const pathStr = path.join("/");

  // ── PROXY everything else to the real API ──────────────────────────────────
  const targetUrl = `${apiBaseUrl}/api/v1/${pathStr}${request.nextUrl.search}`;
  const body =
    request.method === "GET" || request.method === "HEAD"
      ? undefined
      : Buffer.from(await request.arrayBuffer());

  let apiResponse: Response;
  try {
    apiResponse = await fetchWithTimeout(
      targetUrl,
      {
        method: request.method,
        headers: buildProxyHeaders(request),
        body,
        cache: "no-store",
      },
      getProxyTimeoutMs(request.method, pathStr),
    );
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "api_unreachable",
          message: "The Bio API is currently unreachable.",
        },
      },
      { status: 502 },
    );
  }

  const responseHeaders = new Headers();
  const contentType = apiResponse.headers.get("content-type");
  if (contentType) responseHeaders.set("content-type", contentType);
  const setCookie = apiResponse.headers.get("set-cookie");
  if (setCookie) responseHeaders.set("set-cookie", setCookie);

  return new NextResponse(apiResponse.body, {
    status: apiResponse.status,
    headers: responseHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;

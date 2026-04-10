const DEFAULT_SERVER_FETCH_TIMEOUT_MS = 8000;

export async function fetchWithTimeout(
  input: RequestInfo | URL,
  init: RequestInit = {},
  timeoutMs = DEFAULT_SERVER_FETCH_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  const onAbort = () => controller.abort();

  if (init.signal) {
    if (init.signal.aborted) {
      controller.abort();
    } else {
      init.signal.addEventListener("abort", onAbort, { once: true });
    }
  }

  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeoutId);
    if (init.signal) {
      init.signal.removeEventListener("abort", onAbort);
    }
  }
}

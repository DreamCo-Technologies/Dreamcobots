const backendBase = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
const pagesMode = import.meta.env.VITE_GITHUB_PAGES === "true";

function isRelativeBackendPath(value: string): boolean {
  return value.startsWith("/api/") || value === "/api" || value.startsWith("/ws") || value.startsWith("/socket");
}

export function backendUrl(path: string): string {
  if (!pagesMode || !backendBase || !isRelativeBackendPath(path)) return path;
  return `${backendBase}${path}`;
}

export function installBackendBridge(): void {
  if (!pagesMode || !backendBase || typeof window === "undefined") return;

  const nativeFetch = window.fetch.bind(window);
  window.fetch = ((input: RequestInfo | URL, init?: RequestInit) => {
    if (typeof input === "string") return nativeFetch(backendUrl(input), init);
    if (input instanceof URL) {
      if (input.origin === window.location.origin && isRelativeBackendPath(input.pathname)) {
        return nativeFetch(new URL(`${input.pathname}${input.search}${input.hash}`, backendBase), init);
      }
      return nativeFetch(input, init);
    }
    if (input instanceof Request) {
      const url = new URL(input.url, window.location.origin);
      if (url.origin === window.location.origin && isRelativeBackendPath(url.pathname)) {
        const bridged = new URL(`${url.pathname}${url.search}${url.hash}`, backendBase).toString();
        return nativeFetch(new Request(bridged, input), init);
      }
    }
    return nativeFetch(input, init);
  }) as typeof window.fetch;

  const NativeWebSocket = window.WebSocket;
  class BridgedWebSocket extends NativeWebSocket {
    constructor(url: string | URL, protocols?: string | string[]) {
      let target = url.toString();
      if (typeof url === "string" && isRelativeBackendPath(url)) {
        const httpUrl = new URL(url, backendBase);
        httpUrl.protocol = httpUrl.protocol === "https:" ? "wss:" : "ws:";
        target = httpUrl.toString();
      }
      super(target, protocols as string | string[] | undefined);
    }
  }
  window.WebSocket = BridgedWebSocket as typeof WebSocket;
}

export const backendRuntime = {
  pagesMode,
  configured: Boolean(backendBase),
  baseUrl: backendBase,
};
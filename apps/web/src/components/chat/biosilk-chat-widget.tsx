"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type {
  ChatConversationDetail,
  ChatMessage,
  ChatSoilAnalysisInput,
  ChatWidgetConfig,
  SessionResponse,
} from "@bio/api-client";

import { apiClient } from "@/lib/api";

type BioSilkChatWidgetProps = {
  initialSession: SessionResponse | null;
  mode?: "floating" | "embedded";
  forceOpen?: boolean;
};

const DEFAULT_CONFIG: ChatWidgetConfig = {
  id: "local-default",
  heroCtaLabel: "BioSilk Chat",
  heroSubtitle: "Ask about soil health, weather, prices, and crop conditions.",
  launcherLabel: "BioSilk Chat",
  guestTeaserLimit: 4,
  greeting: {
    guestTitle: "BioSilk Chat",
    guestBody: "Ask a basic farming question, or sign in for personalized soil analysis.",
    memberTitle: "Welcome back to BioSilk Chat",
    memberBody: "Ask about your soil, upload crop photos, or request weather and market guidance.",
  },
  quickActions: [
    { id: "soil_analysis", label: "Analyze my soil", guestEnabled: false },
    { id: "soil_history", label: "Explain my last result", guestEnabled: false },
    { id: "pest_diagnosis", label: "Upload crop photo", guestEnabled: true },
    { id: "weather", label: "Weather advice", guestEnabled: true },
    { id: "market_prices", label: "Market prices", guestEnabled: true },
  ],
  theme: {
    accent: "#76c2a4",
    panel: "#ffffff",
  },
};

const QUICK_SOIL_DEFAULTS: ChatSoilAnalysisInput = {
  ph: 6.4,
  organicMatter: 4.5,
  moisture: 42,
  temperature: 21,
  bacteria: 110,
  fungi: 140,
  protozoa: 8,
  nematodes: 85,
  compaction: 250,
  nitrateN: 18,
  soilTexture: "loam",
  productionSystem: "pasture",
};

function launcherIcon(kind: string) {
  switch (kind) {
    case "soil_analysis":
      return "🌱";
    case "weather":
      return "☁️";
    case "market_prices":
      return "📅";
    case "pest_diagnosis":
      return "🤖";
    default:
      return "💬";
  }
}

function formatTime(value: string) {
  try {
    return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

function MinimizeIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M6 12h12" />
    </svg>
  );
}

function guestToken() {
  if (typeof window === "undefined") {
    return null;
  }
  const key = "bioSilkGuestId";
  try {
    const existing = window.localStorage.getItem(key);
    if (existing) {
      return existing;
    }
    const next =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `guest-${Date.now()}`;
    window.localStorage.setItem(key, next);
    return next;
  } catch {
    return null;
  }
}

function SoilQuickForm({
  onSubmit,
  onCancel,
}: {
  onSubmit: (payload: ChatSoilAnalysisInput) => Promise<void>;
  onCancel: () => void;
}) {
  const [values, setValues] = useState(QUICK_SOIL_DEFAULTS);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(values);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-[#f7f2e6] p-4"
    >
      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-[#4e6d44]">
        Quick soil analysis
      </p>
      <div className="grid gap-3 sm:grid-cols-2">
        {[
          ["ph", "pH"],
          ["organicMatter", "Organic matter"],
          ["moisture", "Moisture"],
          ["temperature", "Temperature"],
          ["bacteria", "Bacteria"],
          ["fungi", "Fungi"],
        ].map(([key, label]) => (
          <label key={key} className="text-xs text-[#4a5e40]">
            <span className="mb-1 block font-semibold">{label}</span>
            <input
              type="number"
              step="0.1"
              value={values[key as keyof ChatSoilAnalysisInput] as number}
              onChange={(event) =>
                setValues((current) => ({
                  ...current,
                  [key]: Number.parseFloat(event.target.value) || 0,
                }))
              }
              className="w-full rounded-xl border border-[rgba(58,92,47,0.16)] bg-white px-3 py-2 text-sm text-[#1e3318] outline-none focus:border-[#3a5c2f]"
            />
          </label>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="submit"
          disabled={submitting}
          className="rounded-full bg-[#2f6f58] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#225342] disabled:opacity-60"
        >
          {submitting ? "Running..." : "Run analysis"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-full border border-[rgba(58,92,47,0.16)] px-4 py-2 text-sm font-semibold text-[#35542c]"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

export function BioSilkChatWidget({
  initialSession,
  mode = "floating",
  forceOpen = false,
}: BioSilkChatWidgetProps) {
  const [session] = useState(initialSession);
  const [config, setConfig] = useState<ChatWidgetConfig>(DEFAULT_CONFIG);
  const [open, setOpen] = useState(forceOpen || mode === "embedded");
  const [loading, setLoading] = useState(false);
  const [conversation, setConversation] = useState<ChatConversationDetail | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showSoilForm, setShowSoilForm] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [pendingAttachmentIds, setPendingAttachmentIds] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const userName = session?.user.fullName ?? session?.user.email ?? null;
  const currentGuestToken = useMemo(() => guestToken(), []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    if (window.location.hash === "#biosilk-chat") {
      setOpen(true);
    }
    function handleHashChange() {
      if (window.location.hash === "#biosilk-chat") {
        setOpen(true);
      }
    }
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [conversation?.messages.length, showSoilForm]);

  function closeFloatingChat() {
    setOpen(false);
    setShowSoilForm(false);
    setError(null);
    if (typeof window !== "undefined" && window.location.hash === "#biosilk-chat") {
      window.history.replaceState(null, "", window.location.pathname + window.location.search);
    }
  }

  const ensureChatReady = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const widgetConfig = await apiClient
        .getChatWidgetConfig(currentGuestToken ?? undefined)
        .catch(() => DEFAULT_CONFIG);
      setConfig(widgetConfig);

      const listed = await apiClient
        .listChatConversations(currentGuestToken ?? undefined)
        .catch(() => ({ items: [] }));
      const latest = listed.items[0];
      const activeConversation = latest
        ? await apiClient.getChatConversation(latest.id, currentGuestToken ?? undefined)
        : await apiClient.createChatConversation(
            { channel: "web" },
            currentGuestToken ?? undefined,
          );
      setConversation(activeConversation);
      return activeConversation;
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load BioSilk Chat.");
      return null;
    } finally {
      setLoading(false);
    }
  }, [currentGuestToken]);

  useEffect(() => {
    if (!open) {
      return;
    }
    void ensureChatReady();
  }, [open, ensureChatReady]);

  useEffect(() => {
    const panelVisible = mode === "embedded" || open;
    if (!panelVisible || loading) {
      return;
    }
    textareaRef.current?.focus();
  }, [mode, open, loading]);

  async function refreshConversation(conversationId: string) {
    const next = await apiClient.getChatConversation(
      conversationId,
      currentGuestToken ?? undefined,
    );
    setConversation(next);
    setPendingAttachmentIds([]);
  }

  async function handleSend(customPayload?: {
    content: string;
    quickAction?: string | null;
    toolHint?: string | null;
    metadata?: Record<string, unknown>;
  }) {
    const content = customPayload?.content ?? message.trim();
    if (!content) {
      return;
    }
    let activeConversation = conversation;
    if (!activeConversation) {
      activeConversation = await ensureChatReady();
      if (!activeConversation) {
        return;
      }
    }
    setLoading(true);
    setError(null);
    try {
      await apiClient.sendChatMessage(
        activeConversation.id,
        {
          content,
          quickAction: customPayload?.quickAction ?? null,
          toolHint: customPayload?.toolHint ?? null,
          attachmentIds: pendingAttachmentIds,
          metadata:
            (customPayload?.metadata as Record<string, import("@bio/api-client").JsonValue>) ?? {},
        },
        currentGuestToken ?? undefined,
      );
      setMessage("");
      await refreshConversation(activeConversation.id);
      setShowSoilForm(false);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Message failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleQuickAction(actionId: string) {
    if (actionId === "soil_analysis") {
      if (!session) {
        await handleSend({
          content: "I want a personalized soil analysis.",
          quickAction: "soil_analysis",
        });
        return;
      }
      if (!conversation) {
        const activeConversation = await ensureChatReady();
        if (!activeConversation) {
          return;
        }
      }
      setShowSoilForm(true);
      return;
    }
    if (actionId === "pest_diagnosis") {
      fileInputRef.current?.click();
      return;
    }
    const prompts: Record<string, string> = {
      soil_history: "Explain my last soil result.",
      weather: "I need weather advice for my farm.",
      market_prices: "I want market price guidance for my crop.",
    };
    await handleSend({
      content: prompts[actionId] ?? "Help me with my farm.",
      quickAction: actionId,
    });
  }

  async function handleSoilAnalysis(payload: ChatSoilAnalysisInput) {
    let activeConversation = conversation;
    if (!activeConversation) {
      activeConversation = await ensureChatReady();
      if (!activeConversation) {
        return;
      }
    }
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.runChatSoilAnalysis(payload, currentGuestToken ?? undefined);
      await apiClient.sendChatMessage(
        activeConversation.id,
        {
          content: "Please explain this soil analysis.",
          quickAction: "soil_analysis",
          toolHint: "soil_analysis",
          metadata: {
            measurements: payload as unknown as import("@bio/api-client").JsonValue,
            result: result as unknown as import("@bio/api-client").JsonValue,
          },
        },
        currentGuestToken ?? undefined,
      );
      await refreshConversation(activeConversation.id);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Soil analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  function handleComposerKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey || event.nativeEvent.isComposing) {
      return;
    }
    event.preventDefault();
    if (!loading && message.trim()) {
      void handleSend();
    }
  }

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    let activeConversation = conversation;
    if (!activeConversation) {
      activeConversation = await ensureChatReady();
      if (!activeConversation) {
        return;
      }
    }
    setUploading(true);
    setError(null);
    try {
      const attachment = await apiClient.uploadChatAttachment(
        activeConversation.id,
        file,
        currentGuestToken ?? undefined,
      );
      setPendingAttachmentIds((current) => [...current, attachment.id]);
      await handleSend({
        content: `Please inspect this crop photo: ${file.name}`,
        quickAction: "pest_diagnosis",
        toolHint: "pest_diagnosis",
      });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Upload failed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  const quickActions = config.quickActions.filter((item) => {
    const allowedForGuest = Boolean(item.guestEnabled);
    return session ? true : allowedForGuest;
  });
  const shouldRenderPanel = mode === "embedded" || open;
  const serviceUnavailable = Boolean(error && !loading && !conversation);

  const wrapperClass =
    mode === "embedded"
      ? "relative w-full"
      : "pointer-events-none fixed bottom-2 right-2 z-[1305] sm:bottom-4 sm:right-4";

  const panelClass =
    mode === "embedded"
      ? "relative w-full overflow-hidden rounded-[32px] border border-[rgba(58,92,47,0.14)] bg-[rgba(255,255,255,0.96)] shadow-[0_30px_90px_rgba(20,33,17,0.14)]"
      : `pointer-events-auto relative flex max-h-[calc(100vh-1rem)] w-[min(420px,calc(100vw-1rem))] flex-col overflow-hidden rounded-[28px] border border-[rgba(58,92,47,0.14)] bg-[rgba(255,255,255,0.97)] shadow-[0_30px_90px_rgba(20,33,17,0.18)] transition-all duration-300 sm:max-h-[calc(100vh-2rem)] ${open ? "translate-y-0 opacity-100" : "pointer-events-none translate-y-8 opacity-0"}`;

  return (
    <div id="biosilk-chat" className={wrapperClass}>
      {mode === "floating" && !open ? (
        <button
          type="button"
          onClick={() => {
            setOpen(true);
          }}
          className="pointer-events-auto flex h-16 w-16 items-center justify-center rounded-full border-4 border-white bg-[#8ad2b3] text-2xl shadow-[0_20px_45px_rgba(20,33,17,0.24)] transition-transform hover:scale-105"
          aria-label={config.launcherLabel}
          title={config.launcherLabel}
        >
          {launcherIcon("pest_diagnosis")}
        </button>
      ) : null}

      {shouldRenderPanel ? (
        <div className={panelClass}>
          <div className="border-b border-[rgba(58,92,47,0.12)] bg-[linear-gradient(135deg,#235a46,#77c5a4)] px-6 py-5 text-white">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[rgba(255,255,255,0.72)]">
                  {session ? "Member assistant" : "Guest teaser"}
                </p>
                <h2 className="mt-1 font-serif text-[2rem] leading-none">BioSilk Chat</h2>
                <p className="mt-2 max-w-[260px] text-sm leading-6 text-[rgba(255,255,255,0.88)]">
                  {session ? config.greeting.memberBody : config.greeting.guestBody}
                </p>
              </div>
              {mode === "floating" ? (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={closeFloatingChat}
                    className="flex h-10 w-10 items-center justify-center rounded-full border border-white/30 bg-white/10 text-white transition-colors hover:bg-white/20"
                    aria-label="Minimize chat"
                    title="Minimize chat"
                  >
                    <MinimizeIcon />
                  </button>
                  <Link
                    href="/"
                    onClick={closeFloatingChat}
                    className="flex h-10 w-10 items-center justify-center rounded-full border border-white/30 bg-white/10 text-white transition-colors hover:bg-white/20"
                    aria-label="Back to home"
                    title="Back to home"
                  >
                    <svg
                      aria-hidden="true"
                      viewBox="0 0 24 24"
                      className="h-4 w-4"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M3 11.5 12 4l9 7.5" />
                      <path d="M5 10.5V20h14v-9.5" />
                    </svg>
                  </Link>
                </div>
              ) : null}
            </div>
          </div>

          <div className="border-b border-[rgba(58,92,47,0.08)] bg-[#fbf8f1] px-5 py-4">
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action) => (
                <button
                  key={String(action.id)}
                  type="button"
                  onClick={() => void handleQuickAction(String(action.id))}
                  disabled={loading || uploading}
                  className="rounded-full border border-[rgba(58,92,47,0.12)] bg-white px-3 py-2 text-xs font-semibold text-[#35542c] shadow-sm transition-colors hover:bg-[#f1f8f4]"
                >
                  {String(action.label)}
                </button>
              ))}
            </div>
            {session ? (
              <p className="mt-3 text-xs text-[#61745a]">Signed in as {userName}.</p>
            ) : (
              <p className="mt-3 text-xs text-[#61745a]">
                Guests can ask basic questions. Sign in for saved conversations and personalized
                soil analysis.
              </p>
            )}
          </div>

          <div
            ref={scrollRef}
            className={`space-y-4 overflow-y-auto px-5 py-5 ${
              mode === "embedded" ? "max-h-[420px] min-h-[360px]" : "min-h-[140px] flex-1"
            }`}
          >
            {!conversation && loading ? (
              <p className="text-sm text-[#61745a]">Loading BioSilk Chat…</p>
            ) : null}

            {!conversation?.messages.length ? (
              <div className="rounded-3xl bg-[#f7f2e6] p-4 text-sm leading-6 text-[#54674e]">
                <p className="font-semibold text-[#1e3318]">
                  {session ? config.greeting.memberTitle : config.greeting.guestTitle}
                </p>
                <p className="mt-2">
                  {session ? config.greeting.memberBody : config.greeting.guestBody}
                </p>
              </div>
            ) : null}

            {conversation?.messages.map((item: ChatMessage) => (
              <div
                key={item.id}
                className={`flex ${item.role === "assistant" ? "justify-start" : "justify-end"}`}
              >
                <div
                  className={`max-w-[88%] rounded-[24px] px-4 py-3 text-sm leading-6 shadow-sm ${
                    item.role === "assistant"
                      ? "bg-[#f6f1e4] text-[#314230]"
                      : "bg-[#225a46] text-white"
                  }`}
                >
                  <p>{item.content}</p>
                  {item.citations?.length ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {item.citations.slice(0, 3).map((citation, index) => (
                        <span
                          key={`${item.id}-${index}`}
                          className="rounded-full bg-white/80 px-2.5 py-1 text-[11px] font-semibold text-[#45604a]"
                        >
                          {citation.title}
                        </span>
                      ))}
                    </div>
                  ) : null}
                  <p
                    className={`mt-2 text-[11px] ${item.role === "assistant" ? "text-[#7b8a71]" : "text-white/70"}`}
                  >
                    {formatTime(item.createdAt)}
                  </p>
                </div>
              </div>
            ))}

            {showSoilForm ? (
              <SoilQuickForm
                onSubmit={handleSoilAnalysis}
                onCancel={() => setShowSoilForm(false)}
              />
            ) : null}

            {serviceUnavailable ? (
              <div className="rounded-3xl border border-[rgba(191,75,62,0.16)] bg-[rgba(191,75,62,0.08)] p-4 text-sm leading-6 text-[#7f3b32]">
                <p className="font-semibold text-[#6f291f]">Chat is temporarily unavailable</p>
                <p className="mt-2">
                  The assistant could not start a conversation. This usually means the API or
                  database is degraded. You can retry now or continue browsing the site while the
                  service recovers.
                </p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <button
                    type="button"
                    onClick={() => void ensureChatReady()}
                    className="rounded-full bg-[#225a46] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#1a4637]"
                  >
                    Retry connection
                  </button>
                  <Link
                    href={session ? "/dashboard" : "/contact"}
                    className="rounded-full border border-[rgba(58,92,47,0.16)] bg-white px-4 py-2 text-sm font-semibold text-[#35542c]"
                  >
                    {session ? "Open member dashboard" : "Contact Bio Soil"}
                  </Link>
                </div>
              </div>
            ) : null}

            {error ? (
              <div className="rounded-2xl border border-[rgba(176,79,70,0.18)] bg-[rgba(191,75,62,0.08)] px-4 py-3 text-sm text-[#8d3a30]">
                {error}
              </div>
            ) : null}
          </div>

          <div className="border-t border-[rgba(58,92,47,0.08)] bg-white px-5 py-4">
            {!session ? (
              <div className="mb-3 flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-[#f5f4ef] px-4 py-3">
                <div>
                  <p className="text-sm font-semibold text-[#1e3318]">
                    Want personalized soil guidance?
                  </p>
                  <p className="text-xs text-[#667a60]">
                    Sign in to save analyses and unlock member-only assistant depth.
                  </p>
                </div>
                <Link
                  href="/login"
                  className="rounded-full bg-[#1f5a48] px-4 py-2 text-sm font-semibold text-white"
                >
                  Sign in
                </Link>
              </div>
            ) : null}

            {pendingAttachmentIds.length ? (
              <div className="mb-3 rounded-2xl bg-[#eef6f2] px-4 py-3 text-xs text-[#35542c]">
                Attachment ready. Send your message to analyze the uploaded file.
              </div>
            ) : null}

            <div className="flex items-end gap-3">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-[rgba(58,92,47,0.12)] bg-[#f4f3ef] text-xl text-[#2a4a3b]"
                disabled={uploading || loading || serviceUnavailable}
                aria-label="Upload attachment"
                title="Upload attachment"
              >
                {uploading ? "…" : "＋"}
              </button>
              <div className="flex-1 rounded-[24px] border border-[rgba(58,92,47,0.12)] bg-[#f8f7f2] px-4 py-3">
                <textarea
                  ref={textareaRef}
                  rows={2}
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  onKeyDown={handleComposerKeyDown}
                  placeholder={
                    session
                      ? "Ask BioSilk Chat anything about your soil, crop, weather, or market..."
                      : "Ask a farming question..."
                  }
                  className="w-full resize-none border-0 bg-transparent text-sm text-[#1e3318] outline-none placeholder:text-[#81917d]"
                  disabled={serviceUnavailable}
                />
              </div>
              <button
                type="button"
                onClick={() => void handleSend()}
                disabled={loading || !message.trim() || serviceUnavailable}
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[#235a46] text-xl text-white transition-colors hover:bg-[#1a4637] disabled:opacity-50"
                aria-label="Send message"
                title="Send message"
              >
                ↑
              </button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,.pdf,.csv,.xlsx"
              onChange={(event) => void handleUpload(event)}
              className="hidden"
            />
          </div>
        </div>
      ) : null}
    </div>
  );
}

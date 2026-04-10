"use client";

type AdminAsyncStateProps = {
  title: string;
  description: string;
  variant?: "loading" | "error" | "empty";
  actionLabel?: string;
  onAction?: () => void;
};

const toneMap = {
  loading: {
    border: "border-[rgba(168,204,138,0.14)]",
    background: "bg-[rgba(255,255,255,0.03)]",
    badge: "Loading",
    badgeTone: "bg-[rgba(168,204,138,0.12)] text-[#a8cc8a]",
  },
  error: {
    border: "border-[rgba(191,75,62,0.16)]",
    background: "bg-[rgba(191,75,62,0.08)]",
    badge: "Needs attention",
    badgeTone: "bg-[rgba(191,75,62,0.14)] text-[#ffb3a9]",
  },
  empty: {
    border: "border-[rgba(168,204,138,0.12)]",
    background: "bg-[rgba(255,255,255,0.03)]",
    badge: "Empty",
    badgeTone: "bg-[rgba(168,204,138,0.12)] text-[#a8cc8a]",
  },
} as const;

export function AdminAsyncState({
  title,
  description,
  variant = "loading",
  actionLabel,
  onAction,
}: AdminAsyncStateProps) {
  const tone = toneMap[variant];

  return (
    <div
      className={`rounded-3xl border px-6 py-8 ${tone.border} ${tone.background}`}
      role={variant === "error" ? "alert" : "status"}
    >
      <span
        className={`inline-flex rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${tone.badgeTone}`}
      >
        {tone.badge}
      </span>
      <h2 className="mt-4 font-serif text-2xl text-white">{title}</h2>
      <p className="mt-3 max-w-2xl text-sm leading-7 text-[#8ea184]">{description}</p>
      {actionLabel && onAction ? (
        <button
          type="button"
          onClick={onAction}
          className="mt-5 rounded-full border border-[rgba(168,204,138,0.2)] bg-[rgba(58,92,47,0.36)] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[rgba(58,92,47,0.5)]"
        >
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}

import { cn } from "../lib/cn";

const statusClasses: Record<string, string> = {
  queued: "bg-mineral-100 text-mineral-800",
  running: "bg-copper-100 text-copper-900",
  succeeded: "bg-sage-100 text-sage-900",
  failed: "bg-red-100 text-red-800",
  canceled: "bg-mineral-200 text-mineral-900",
  cancel_requested: "bg-sand-200 text-sand-900",
  draft: "bg-mineral-100 text-mineral-800",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em]",
        statusClasses[status] ?? "bg-mineral-100 text-mineral-900",
      )}
    >
      {status.replaceAll("_", " ")}
    </span>
  );
}

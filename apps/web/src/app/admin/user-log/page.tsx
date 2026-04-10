"use client";

import { useEffect, useState } from "react";

import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { adminApi } from "@/lib/adminApi";
import type { UserActivityLogEntry } from "@/lib/adminTypes";

export default function AdminUserLogPage() {
  const [items, setItems] = useState<UserActivityLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadLog() {
    setLoading(true);
    try {
      const response = await adminApi.listUserLog();
      setItems(response.items);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load user activity.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadLog();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Loading activity log"
          description="Pulling recent sign-ins, account changes, and system activity."
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Activity log is unavailable"
          description={error}
          variant="error"
          actionLabel="Retry"
          onAction={() => void loadLog()}
        />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl">
      <div className="mb-8">
        <p className="text-[#5a8050] text-xs font-semibold uppercase tracking-[0.2em] mb-2">
          Admin
        </p>
        <h1 className="font-serif text-3xl text-white">User Log</h1>
        <p className="text-[#5a7050] text-sm mt-1">
          Recent sign-ins, sign-ups, and workflow activity across the organization
        </p>
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={`${item.activityType}-${item.happenedAt}-${item.userEmail ?? "system"}-${item.details ?? ""}`}
            className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-4"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-white">{item.activityLabel}</p>
                <p className="text-sm text-[#a8cc8a]">{item.userEmail ?? "System"}</p>
              </div>
              <p className="text-xs uppercase tracking-[0.14em] text-[#5a8050]">
                {new Date(item.happenedAt).toLocaleString()}
              </p>
            </div>
            {item.details ? (
              <p className="mt-2 text-sm leading-6 text-[#7a9a6a]">{item.details}</p>
            ) : null}
          </div>
        ))}
        {items.length === 0 ? (
          <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] p-8 text-center text-[#5a7050]">
            No activity has been recorded yet.
          </div>
        ) : null}
      </div>
    </div>
  );
}

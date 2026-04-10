"use client";

import { useEffect, useState } from "react";
import type { ChatAdminConfig } from "@bio/api-client";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { apiClient } from "@/lib/api";
import { getApiErrorMessage } from "@/lib/api-errors";

export default function ChatConfigOverview() {
  const [config, setConfig] = useState<ChatAdminConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const data = await apiClient.getAdminChatConfig();
      setConfig(data);
      setError(null);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load chat configuration."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  if (loading) {
    return (
      <AdminAsyncState
        title="Loading chat configuration"
        description="Fetching the active assistant and widget settings."
      />
    );
  }

  if (error || !config) {
    return (
      <AdminAsyncState
        title="Chat configuration is unavailable"
        description={
          error ??
          "The assistant config could not be loaded. Check your chat provider setup, API health, and database connection."
        }
        variant="error"
        actionLabel="Retry"
        onAction={() => void load()}
      />
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-[#1e3318] mb-4">Configuration Overview</h2>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="bg-white p-6 rounded-2xl border border-[rgba(30, 60, 20, 0.12)]">
          <h3 className="font-semibold text-lg text-[#1e3318] mb-4">Active Assistant</h3>
          {config.activeAssistant ? (
            <div className="space-y-3">
              <p className="text-sm">
                <span className="font-medium">Name:</span> {config.activeAssistant.name}
              </p>
              <p className="text-sm">
                <span className="font-medium">Provider:</span> {config.activeAssistant.provider}
              </p>
              <p className="text-sm">
                <span className="font-medium">Model:</span> {config.activeAssistant.model}
              </p>
              <p className="text-sm">
                <span className="font-medium">Access Mode:</span>{" "}
                {config.activeAssistant.accessMode}
              </p>
            </div>
          ) : (
            <p className="text-sm text-gray-500 italic">No active assistant configured.</p>
          )}
        </div>

        <div className="bg-white p-6 rounded-2xl border border-[rgba(58,92,47,0.12)]">
          <h3 className="font-semibold text-lg text-[#1e3318] mb-4">Widget Configuration</h3>
          <div className="space-y-3">
            <p className="text-sm">
              <span className="font-medium">Hero CTA:</span> {config.widget.heroCtaLabel}
            </p>
            <p className="text-sm">
              <span className="font-medium">Launcher:</span> {config.widget.launcherLabel}
            </p>
            <p className="text-sm">
              <span className="font-medium">Guest Limit:</span> {config.widget.guestTeaserLimit}{" "}
              messages
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

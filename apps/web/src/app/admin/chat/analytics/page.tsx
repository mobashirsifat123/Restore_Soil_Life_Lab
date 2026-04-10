"use client";

import { useEffect, useState } from "react";
import type { ChatAdminConfig } from "@bio/api-client";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { apiClient } from "@/lib/api";
import { getApiErrorMessage } from "@/lib/api-errors";

export default function ChatAnalytics() {
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
      setError(getApiErrorMessage(err, "Failed to load analytics."));
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
        title="Loading chat analytics"
        description="Collecting conversation volume and assistant quality metrics."
      />
    );
  }

  if (error) {
    return (
      <AdminAsyncState
        title="Chat analytics are unavailable"
        description={error}
        variant="error"
        actionLabel="Retry"
        onAction={() => void load()}
      />
    );
  }

  const stats = config?.analytics;

  return (
    <div>
      <h2 className="text-xl font-semibold text-[#1e3318] mb-4">Analytics</h2>
      <div className="bg-white p-6 rounded-2xl border border-[rgba(58,92,47,0.12)]">
        <h3 className="font-semibold text-lg text-[#1e3318] mb-4">Volume & Quality Summary</h3>
        <p className="text-sm text-[#5a7050] mb-6">Real-time assistant performance metrics.</p>

        {stats ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="p-5 border border-[rgba(58,92,47,0.12)] rounded-xl bg-[#fbf8f1]">
              <p className="text-3xl font-serif font-bold text-[#3a5c2f]">
                {stats.conversationCount}
              </p>
              <p className="text-sm text-[#5a7050] mt-1 font-medium">Conversations</p>
            </div>
            <div className="p-5 border border-[rgba(58,92,47,0.12)] rounded-xl bg-[#fbf8f1]">
              <p className="text-3xl font-serif font-bold text-[#3a5c2f]">{stats.messageCount}</p>
              <p className="text-sm text-[#5a7050] mt-1 font-medium">Messages</p>
            </div>
            <div className="p-5 border border-[rgba(58,92,47,0.12)] rounded-xl bg-[#fbf8f1]">
              <p className="text-3xl font-serif font-bold text-[#d4933d]">
                {stats.lowConfidenceCount}
              </p>
              <p className="text-sm text-[#5a7050] mt-1 font-medium">Low Confidence</p>
            </div>
            <div className="p-5 border border-[rgba(58,92,47,0.12)] rounded-xl bg-[#fbf8f1]">
              <p className="text-3xl font-serif font-bold text-red-600">{stats.failedToolRuns}</p>
              <p className="text-sm text-[#5a7050] mt-1 font-medium">Failed Tool Runs</p>
            </div>
          </div>
        ) : null}

        <div className="h-64 bg-gray-50 border border-[rgba(58,92,47,0.12)] flex items-center justify-center rounded-xl">
          <p className="text-sm text-[#5a7050]">Usage trend charts coming soon</p>
        </div>
      </div>
    </div>
  );
}

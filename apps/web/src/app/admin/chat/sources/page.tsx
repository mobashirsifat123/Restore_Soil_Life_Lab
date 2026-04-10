"use client";

import { useEffect, useState } from "react";
import type { ChatKnowledgeSource } from "@bio/api-client";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { apiClient } from "@/lib/api";
import { getApiErrorMessage } from "@/lib/api-errors";

export default function KnowledgeSources() {
  const [sources, setSources] = useState<ChatKnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const data = await apiClient.listAdminChatSources();
      setSources(data);
      setError(null);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load sources."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function handleReindex(id: string) {
    try {
      await apiClient.reindexAdminChatSource(id);
      alert("Source reindexed successfully.");
    } catch (err) {
      alert(getApiErrorMessage(err, "Failed to reindex source."));
    }
  }

  if (loading) {
    return (
      <AdminAsyncState
        title="Loading knowledge sources"
        description="Fetching the source library that grounds assistant answers."
      />
    );
  }

  if (error) {
    return (
      <AdminAsyncState
        title="Knowledge sources are unavailable"
        description={error}
        variant="error"
        actionLabel="Retry"
        onAction={() => void load()}
      />
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-[#1e3318] mb-4">Knowledge Sources</h2>
      <div className="bg-white p-6 rounded-2xl border border-[rgba(58,92,47,0.12)]">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg text-[#1e3318]">Sources</h3>
          <button className="px-4 py-2 bg-[#3a5c2f] text-white rounded-lg text-sm">
            Add Source
          </button>
        </div>
        <p className="text-sm text-[#5a7050] mb-6">
          Manage knowledge sources to ground the assistant.
        </p>

        {sources.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No sources found.</p>
        ) : (
          <div className="space-y-4">
            {sources.map((source) => (
              <div
                key={source.id}
                className="flex items-center justify-between p-4 border border-[rgba(58,92,47,0.12)] rounded-xl"
              >
                <div>
                  <h4 className="font-semibold text-[#1e3318]">{source.title}</h4>
                  <p className="text-xs text-[#5a7050] uppercase mt-1 tracking-wider">
                    {source.sourceType}
                  </p>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => void handleReindex(source.id)}
                    className="text-xs px-3 py-1.5 border border-[#3a5c2f] text-[#3a5c2f] rounded-lg hover:bg-[#f1f8f4]"
                  >
                    Reindex
                  </button>
                  <span
                    className={`text-xs px-3 py-1.5 rounded-lg ${source.isEnabled ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}
                  >
                    {source.isEnabled ? "Enabled" : "Disabled"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

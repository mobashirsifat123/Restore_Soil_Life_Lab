"use client";

import { useEffect, useState } from "react";
import type { ChatAdminConfig } from "@bio/api-client";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { apiClient } from "@/lib/api";
import { getApiErrorMessage } from "@/lib/api-errors";

export default function PromptLab() {
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
        title="Loading prompt lab"
        description="Fetching the active prompt pack so you can inspect grounding and tone."
      />
    );
  }

  if (error) {
    return (
      <AdminAsyncState
        title="Prompt lab is unavailable"
        description={error}
        variant="error"
        actionLabel="Retry"
        onAction={() => void load()}
      />
    );
  }

  if (!config || !config.activeAssistant) {
    return (
      <AdminAsyncState
        title="No active assistant found"
        description="Create or activate an assistant before reviewing prompts here."
        variant="empty"
      />
    );
  }

  const prompts = [
    { label: "General Assistant", content: config.activeAssistant.promptPack.generalPrompt },
    { label: "Soil Analysis", content: config.activeAssistant.promptPack.soilPrompt },
    { label: "Pest Diagnosis", content: config.activeAssistant.promptPack.pestPrompt },
    { label: "Market Prices", content: config.activeAssistant.promptPack.marketPrompt },
    { label: "Weather Advisories", content: config.activeAssistant.promptPack.weatherPrompt },
  ];

  return (
    <div>
      <h2 className="text-xl font-semibold text-[#1e3318] mb-4">Prompt Lab</h2>
      <div className="bg-white p-6 rounded-2xl border border-[rgba(58,92,47,0.12)]">
        <h3 className="font-semibold text-lg text-[#1e3318] mb-4">Versioned Prompts</h3>
        <p className="text-sm text-[#5a7050] mb-6">
          Review current system prompts for the active assistant.
        </p>

        <div className="space-y-6">
          {prompts.map((p, i) => (
            <div key={i} className="border border-[rgba(58,92,47,0.12)] rounded-xl overflow-hidden">
              <div className="bg-[#fbf8f1] px-4 py-3 border-b border-[rgba(58,92,47,0.12)]">
                <h4 className="font-semibold text-sm text-[#1e3318]">{p.label}</h4>
              </div>
              <div className="p-4 bg-gray-50">
                <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                  {p.content || "No prompt configured."}
                </pre>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

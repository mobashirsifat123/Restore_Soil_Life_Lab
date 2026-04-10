"use client";

import { useEffect, useState } from "react";
import type { ChatAdminConfig } from "@bio/api-client";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { apiClient } from "@/lib/api";
import { getApiErrorMessage } from "@/lib/api-errors";

export default function ChatTools() {
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
      setError(getApiErrorMessage(err, "Failed to load tool configuration."));
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
        title="Loading assistant tools"
        description="Checking which tools are currently enabled for the active assistant."
      />
    );
  }

  if (error) {
    return (
      <AdminAsyncState
        title="Tool configuration is unavailable"
        description={error}
        variant="error"
        actionLabel="Retry"
        onAction={() => void load()}
      />
    );
  }

  const enabledTools = config?.activeAssistant?.enabledTools || [];

  const allTools = [
    { id: "soil_analysis", name: "Soil Analysis", description: "Execute active SilkSoil formulas" },
    {
      id: "soil_history",
      name: "Soil History",
      description: "Retrieve member's past analysis results",
    },
    {
      id: "weather",
      name: "Weather",
      description: "Fetch localized weather forecasts and advisories",
    },
    {
      id: "market_prices",
      name: "Market Prices",
      description: "Fetch regional crop market prices",
    },
    {
      id: "pest_diagnosis",
      name: "Pest Diagnosis",
      description: "Image-based pest and disease classifier",
    },
    {
      id: "knowledge_search",
      name: "Knowledge Search",
      description: "Retrieve admin-managed CMS pages and documents",
    },
  ];

  return (
    <div>
      <h2 className="text-xl font-semibold text-[#1e3318] mb-4">Tools Configuration</h2>
      <div className="bg-white p-6 rounded-2xl border border-[rgba(58,92,47,0.12)]">
        <h3 className="font-semibold text-lg text-[#1e3318] mb-4">Available Tools</h3>
        <p className="text-sm text-[#5a7050] mb-6">
          These tools are bound to the currently active assistant.
        </p>

        <div className="grid gap-4 md:grid-cols-2">
          {allTools.map((tool) => {
            const isEnabled = enabledTools.includes(tool.id);
            return (
              <div
                key={tool.id}
                className={`p-4 border rounded-xl flex items-start gap-4 ${isEnabled ? "border-[rgba(58,92,47,0.3)] bg-[#fbf8f1]" : "border-gray-200 bg-gray-50"}`}
              >
                <div
                  className={`mt-1 h-4 w-4 rounded-full border-2 ${isEnabled ? "border-[#3a5c2f] bg-[#3a5c2f]" : "border-gray-300"}`}
                />
                <div>
                  <h4 className={`font-semibold ${isEnabled ? "text-[#1e3318]" : "text-gray-500"}`}>
                    {tool.name}
                  </h4>
                  <p className="text-xs text-[#5a7050] mt-1">{tool.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

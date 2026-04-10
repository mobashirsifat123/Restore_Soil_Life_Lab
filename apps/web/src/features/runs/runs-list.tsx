"use client";

import Link from "next/link";
import { Button, PageHeader, Panel, StatusBadge } from "@bio/ui";
import { useRunsQuery } from "../../hooks/use-bio-queries";

export function RunsList() {
  const { data, isLoading, isError } = useRunsQuery();

  if (isLoading) {
    return <Panel className="text-[#5d624e]">Loading runs...</Panel>;
  }

  if (isError) {
    return <Panel className="border-red-200 text-red-800">Failed to load run history.</Panel>;
  }

  const runs = data?.items || [];

  return (
    <div className="space-y-10">
      <PageHeader
        eyebrow="Run History"
        title="Simulation Runs"
        actions={
          <Link href="/projects">
            <Button>New Run via Project</Button>
          </Link>
        }
      >
        View and download results from all previous scientific simulations.
      </PageHeader>

      <Panel className="p-0 overflow-hidden">
        {runs.length === 0 ? (
          <div className="p-10 text-center text-[#5d624e]">
            <p>No simulation runs found.</p>
            <Link href="/projects" className="mt-4 inline-block text-[#3a5c2f] hover:underline">
              Start by creating a project and scenario
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-[#f5efdf] text-[#283422]">
                <tr>
                  <th className="px-6 py-4 font-semibold">Run ID</th>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold">Engine</th>
                  <th className="px-6 py-4 font-semibold">Created</th>
                  <th className="px-6 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#e2e8f0]">
                {runs.map((run) => (
                  <tr key={run.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs text-[#5d624e]">
                      {run.id.slice(0, 8)}...
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={run.status} />
                    </td>
                    <td className="px-6 py-4 text-[#5d624e]">
                      {run.engineName} v{run.engineVersion}
                    </td>
                    <td className="px-6 py-4 text-[#5d624e]">
                      {new Date(run.createdAt).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href={`/runs/${run.id}`}>
                        <Button variant="ghost" className="text-sm py-1 h-auto">
                          View details
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </div>
  );
}

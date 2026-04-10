"use client";

import Link from "next/link";
import * as XLSX from "xlsx";

import { Button, PageHeader, Panel, StatusBadge } from "@bio/ui";

import { useRunQuery, useRunResultsQuery, useRunStatusQuery } from "../../hooks/use-bio-queries";
import { getApiErrorMessage } from "../../lib/api-errors";

export function RunDetailView({ runId }: { runId: string }) {
  const runQuery = useRunQuery(runId);
  const statusQuery = useRunStatusQuery(runId);
  const resultsQuery = useRunResultsQuery(runId, Boolean(statusQuery.data));

  const handleExportCSV = () => {
    if (!resultsQuery.data?.resultSummary) return;
    const summary = resultsQuery.data.resultSummary;
    const worksheet = XLSX.utils.json_to_sheet([summary]);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Result Summary");
    XLSX.writeFile(workbook, `run_${runId}_summary.csv`);
  };

  if (runQuery.isLoading || statusQuery.isLoading) {
    return <Panel className="text-[#5d624e]">Loading run status...</Panel>;
  }

  if (runQuery.isError || statusQuery.isError) {
    const error = runQuery.error ?? statusQuery.error;
    return (
      <Panel className="border-red-200 text-red-800">
        Failed to load run details. {getApiErrorMessage(error, "Unknown error.")}
      </Panel>
    );
  }

  if (!runQuery.data || !statusQuery.data) {
    return <Panel className="text-[#5d624e]">Run not found.</Panel>;
  }

  return (
    <div className="space-y-10">
      <PageHeader
        eyebrow="Simulation Run"
        title={`Run ${runQuery.data.id.slice(0, 8)}`}
        actions={
          <Link href={`/projects/${runQuery.data.projectId}`}>
            <Button variant="secondary">Back to project</Button>
          </Link>
        }
      >
        <div className="flex flex-wrap items-center gap-3">
          <StatusBadge status={statusQuery.data.status} />
          <span className="font-mono text-caption uppercase tracking-[0.16em] text-[#7c7a67]">
            {runQuery.data.engineName} {runQuery.data.engineVersion}
          </span>
        </div>
      </PageHeader>

      <div className="grid gap-4 xl:grid-cols-4">
        <Panel className="space-y-2">
          <p className="editorial-kicker font-mono text-xs">Lifecycle</p>
          <p className="font-serif text-4xl tracking-[-0.03em] text-[#283422]">
            {statusQuery.data.status}
          </p>
          <p className="text-sm leading-6 text-[#5d624e]">
            Status updates poll every two seconds until the worker reaches a terminal state.
          </p>
        </Panel>
        <Panel className="space-y-2">
          <p className="editorial-kicker font-mono text-xs">Parameter set</p>
          <p className="font-serif text-4xl tracking-[-0.03em] text-[#283422]">
            v{runQuery.data.parameterSetVersion}
          </p>
          <p className="text-sm leading-6 text-[#5d624e]">Snapshot-pinned for reproducibility.</p>
        </Panel>
        <Panel className="space-y-2">
          <p className="editorial-kicker font-mono text-xs">Soil sample</p>
          <p className="font-serif text-4xl tracking-[-0.03em] text-[#283422]">
            v{runQuery.data.soilSampleVersion}
          </p>
          <p className="text-sm leading-6 text-[#5d624e]">
            Pinned to the immutable sample version used for this run.
          </p>
        </Panel>
        <Panel className="space-y-2">
          <p className="editorial-kicker font-mono text-xs">Schema</p>
          <p className="font-serif text-4xl tracking-[-0.03em] text-[#283422]">
            {runQuery.data.inputSchemaVersion}
          </p>
          <p className="text-sm leading-6 text-[#5d624e]">
            Engine input contract version used for this run.
          </p>
        </Panel>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <Panel className="space-y-4">
          <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">Lifecycle</h2>
          <dl className="space-y-3 text-sm leading-6 text-[#5d624e]">
            <div>
              <dt className="font-semibold text-[#283422]">Queued at</dt>
              <dd>{statusQuery.data.queuedAt || "Pending"}</dd>
            </div>
            <div>
              <dt className="font-semibold text-[#283422]">Started at</dt>
              <dd>{statusQuery.data.startedAt || "Not started yet"}</dd>
            </div>
            <div>
              <dt className="font-semibold text-[#283422]">Completed at</dt>
              <dd>{statusQuery.data.completedAt || "Not completed yet"}</dd>
            </div>
            <div>
              <dt className="font-semibold text-[#283422]">Input hash</dt>
              <dd className="break-all font-mono text-xs">{runQuery.data.inputHash}</dd>
            </div>
            <div>
              <dt className="font-semibold text-[#283422]">Result hash</dt>
              <dd className="break-all font-mono text-xs">
                {runQuery.data.resultHash || "Pending worker completion"}
              </dd>
            </div>
            {statusQuery.data.failureMessage ? (
              <div>
                <dt className="font-semibold text-red-800">Failure</dt>
                <dd className="text-red-700">{statusQuery.data.failureMessage}</dd>
              </div>
            ) : null}
          </dl>
        </Panel>

        <Panel className="space-y-4">
          <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">Result metadata</h2>
          {resultsQuery.isLoading ? (
            <p className="text-sm text-[#5d624e]">Loading result payload...</p>
          ) : null}
          {resultsQuery.isError ? (
            <p className="text-sm text-red-700">
              {getApiErrorMessage(resultsQuery.error, "Failed to load results.")}
            </p>
          ) : null}
          <dl className="space-y-3 text-sm leading-6 text-[#5d624e]">
            <div>
              <dt className="font-semibold text-[#283422]">Engine</dt>
              <dd>
                {runQuery.data.engineName} {runQuery.data.engineVersion}
              </dd>
            </div>
            <div>
              <dt className="font-semibold text-[#283422]">Input hash</dt>
              <dd className="break-all font-mono text-xs">
                {resultsQuery.data?.inputHash ?? runQuery.data.inputHash}
              </dd>
            </div>
            <div>
              <dt className="font-semibold text-[#283422]">Result hash</dt>
              <dd className="break-all font-mono text-xs">
                {resultsQuery.data?.resultHash || "Pending worker completion"}
              </dd>
            </div>
          </dl>
        </Panel>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel className="space-y-4 relative">
          <div className="flex justify-between items-center">
            <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
              Result summary
            </h2>
            {resultsQuery.data?.resultSummary && (
              <Button variant="secondary" onClick={handleExportCSV}>
                Download CSV
              </Button>
            )}
          </div>
          {resultsQuery.data?.resultSummary ? (
            <pre className="overflow-x-auto rounded-md bg-mineral-950 p-4 text-xs text-sand-50">
              {JSON.stringify(resultsQuery.data.resultSummary, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-[#5d624e]">
              Result summary will appear once the worker completes the run.
            </p>
          )}
        </Panel>

        <Panel className="space-y-4">
          <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">Artifacts</h2>
          {resultsQuery.data?.artifacts.length ? (
            <ul className="space-y-3 text-sm text-[#5d624e]">
              {resultsQuery.data.artifacts.map((artifact) => (
                <li
                  key={artifact.id}
                  className="rounded-[20px] border border-[rgba(72,85,59,0.14)] bg-[rgba(255,255,255,0.48)] p-4"
                >
                  <p className="font-semibold text-[#283422]">{artifact.label}</p>
                  <p className="font-mono text-xs text-[#7c7a67]">{artifact.storageKey}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[#5d624e]">
              Artifacts will be listed here after processing.
            </p>
          )}
        </Panel>
      </div>

      <Panel className="space-y-4">
        <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">Input snapshot</h2>
        <pre className="overflow-x-auto rounded-md bg-mineral-950 p-4 text-xs text-sand-50">
          {JSON.stringify(resultsQuery.data?.inputSnapshot ?? {}, null, 2)}
        </pre>
      </Panel>
    </div>
  );
}

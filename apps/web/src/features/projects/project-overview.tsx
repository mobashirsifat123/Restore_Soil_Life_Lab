"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { Button, PageHeader, Panel } from "@bio/ui";

import {
  useCreateRunMutation,
  useProjectQuery,
  useScenariosQuery,
  useSoilSamplesQuery,
} from "../../hooks/use-bio-queries";
import { getApiErrorMessage } from "../../lib/api-errors";

export function ProjectOverview({ projectId }: { projectId: string }) {
  const router = useRouter();
  const projectQuery = useProjectQuery(projectId);
  const soilSamplesQuery = useSoilSamplesQuery(projectId);
  const scenariosQuery = useScenariosQuery(projectId);

  const createRun = useCreateRunMutation(projectId, {
    onSuccess: (run) => {
      router.push(`/runs/${run.id}`);
    },
  });

  const loading = projectQuery.isLoading || soilSamplesQuery.isLoading || scenariosQuery.isLoading;
  const error = projectQuery.error ?? soilSamplesQuery.error ?? scenariosQuery.error;

  if (loading) {
    return <Panel className="text-[#5d624e]">Loading project workspace...</Panel>;
  }

  if (error) {
    return (
      <Panel className="border-red-200 text-red-800">
        Failed to load project data. {getApiErrorMessage(error, "Unknown error.")}
      </Panel>
    );
  }

  if (!projectQuery.data) {
    return <Panel className="text-[#5d624e]">Project not found.</Panel>;
  }

  const soilSamples = soilSamplesQuery.data?.items ?? [];
  const scenarios = scenariosQuery.data?.items ?? [];
  const canCreateScenario = soilSamples.length > 0;

  function handleCreateRun(scenarioId: string) {
    createRun.mutate({
      scenarioId,
      idempotencyKey: crypto.randomUUID(),
      executionOptions: {
        timeoutSeconds: 120,
        requestedModules: ["flux", "mineralization", "stability", "dynamics", "decomposition"],
      },
    });
  }

  return (
    <div className="space-y-10">
      <PageHeader
        eyebrow="Project Workspace"
        title={projectQuery.data.name}
        actions={
          <>
            <Link href={`/projects/${projectId}/samples/new`}>
              <Button variant="secondary">Add sample</Button>
            </Link>
            {canCreateScenario ? (
              <Link href={`/projects/${projectId}/scenarios/new`}>
                <Button>Create scenario</Button>
              </Link>
            ) : (
              <Button disabled>Create scenario</Button>
            )}
          </>
        }
      >
        {projectQuery.data.description ||
          "Use this workspace to move from measured soil inputs into versioned scenarios and reproducible runs."}
      </PageHeader>

      <div className="grid gap-5 xl:grid-cols-3">
        <Panel className="space-y-3">
          <p className="editorial-kicker font-mono text-xs">Foundation</p>
          <h2 className="font-serif text-[2rem] tracking-[-0.03em] text-[#283422]">
            Stable project record
          </h2>
          <p className="text-sm leading-6 text-[#5d624e]">
            The project is the parent container for soil samples, scenarios, and the resulting run
            history.
          </p>
        </Panel>
        <Panel className="space-y-3">
          <p className="editorial-kicker font-mono text-xs">Scientific input</p>
          <h2 className="font-serif text-[2rem] tracking-[-0.03em] text-[#283422]">
            Versioned soil samples
          </h2>
          <p className="text-sm leading-6 text-[#5d624e]">
            Samples now preserve stable identities and immutable scientific versions for scenario
            pinning and exact run provenance.
          </p>
        </Panel>
        <Panel className="space-y-3">
          <p className="editorial-kicker font-mono text-xs">Execution</p>
          <h2 className="font-serif text-[2rem] tracking-[-0.03em] text-[#283422]">
            Worker-backed runs
          </h2>
          <p className="text-sm leading-6 text-[#5d624e]">
            Submit a deterministic run from a scenario and inspect status, result metadata, and
            artifacts from the browser.
          </p>
        </Panel>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.92fr_1.08fr]">
        <Panel className="space-y-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="editorial-kicker font-mono text-xs">Measured inputs</p>
              <h2 className="mt-2 font-serif text-3xl tracking-[-0.03em] text-[#283422]">
                Soil samples
              </h2>
            </div>
            <Link
              href={`/projects/${projectId}/samples/new`}
              className="text-sm font-semibold text-[#556347]"
            >
              Add sample
            </Link>
          </div>

          {soilSamples.length ? (
            <div className="space-y-3">
              {soilSamples.map((soilSample) => (
                <div
                  key={soilSample.id}
                  className="rounded-[22px] border border-[rgba(72,85,59,0.14)] bg-[rgba(255,255,255,0.52)] p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <p className="font-serif text-2xl tracking-[-0.03em] text-[#283422]">
                        {soilSample.sampleCode}
                      </p>
                      <p className="text-sm leading-6 text-[#5d624e]">
                        {soilSample.name || "Unnamed sample"}
                      </p>
                    </div>
                    <span className="rounded-full bg-[rgba(85,99,71,0.1)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-[#556347]">
                      v{soilSample.currentVersion}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-sm leading-6 text-[#5d624e]">
                No samples have been added yet. Start with a measured soil record so scenarios can
                reference pinned scientific data.
              </p>
              <Link href={`/projects/${projectId}/samples/new`}>
                <Button variant="secondary">Create first sample</Button>
              </Link>
            </div>
          )}
        </Panel>

        <Panel className="space-y-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="editorial-kicker font-mono text-xs">Scenario design</p>
              <h2 className="mt-2 font-serif text-3xl tracking-[-0.03em] text-[#283422]">
                Scenarios and runs
              </h2>
            </div>
            <Link
              href={`/projects/${projectId}/scenarios/new`}
              className="text-sm font-semibold text-[#556347]"
            >
              Create scenario
            </Link>
          </div>

          {!soilSamples.length ? (
            <p className="text-sm leading-6 text-[#5d624e]">
              Add a soil sample first. Scenarios are pinned to exact sample versions and cannot be
              built without at least one measured input.
            </p>
          ) : scenarios.length ? (
            <div className="space-y-4">
              {scenarios.map((scenario) => (
                <div
                  key={scenario.id}
                  className="space-y-4 rounded-[24px] border border-[rgba(72,85,59,0.14)] bg-[rgba(255,255,255,0.52)] p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <p className="font-serif text-2xl tracking-[-0.03em] text-[#283422]">
                        {scenario.name}
                      </p>
                      <p className="text-sm leading-6 text-[#5d624e]">
                        {scenario.description || "No description yet."}
                      </p>
                    </div>
                    <span className="rounded-full bg-[rgba(72,85,59,0.08)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-[#556347]">
                      v{scenario.version}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <p className="text-sm text-[#7c7a67]">
                      Pinned to sample version {scenario.soilSampleVersionId.slice(0, 8)}.
                    </p>
                    <Button
                      disabled={createRun.isPending}
                      onClick={() => {
                        handleCreateRun(scenario.id);
                      }}
                    >
                      {createRun.isPending ? "Submitting..." : "Submit simulation run"}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-sm leading-6 text-[#5d624e]">
                No scenarios yet. Build the first versioned scenario from the measured soil sample
                and baseline food web assumptions.
              </p>
              <Link href={`/projects/${projectId}/scenarios/new`}>
                <Button>Create first scenario</Button>
              </Link>
            </div>
          )}

          {createRun.isError ? (
            <p className="text-sm text-red-700">
              {getApiErrorMessage(createRun.error, "Failed to submit simulation run.")}
            </p>
          ) : null}
        </Panel>
      </div>
    </div>
  );
}

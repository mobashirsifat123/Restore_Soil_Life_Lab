"use client";

import type { ScenarioCreate } from "@bio/api-client";
import { useRouter } from "next/navigation";
import { ChangeEvent, FormEvent, useMemo, useState } from "react";

import { Button, Input, PageHeader, Panel, Textarea } from "@bio/ui";

import { useCreateScenarioMutation, useSoilSamplesQuery } from "../../hooks/use-bio-queries";
import { getApiErrorMessage } from "../../lib/api-errors";
import { parseJsonObject, parseJsonValue } from "../../lib/json";

const defaultFoodWeb = JSON.stringify(
  {
    name: "Baseline food web",
    description: "Simple placeholder web for the first implementation slice.",
    nodes: [
      {
        key: "detritus",
        label: "Detritus",
        trophicGroup: "detritus",
        biomassCarbon: 100,
        biomassNitrogen: 12,
        isDetritus: true,
      },
      {
        key: "bacteria",
        label: "Bacteria",
        trophicGroup: "microbe",
        biomassCarbon: 42,
        biomassNitrogen: 8,
      },
      {
        key: "fungi",
        label: "Fungi",
        trophicGroup: "fungi",
        biomassCarbon: 58,
        biomassNitrogen: 10,
      },
    ],
    links: [
      { source: "detritus", target: "bacteria", weight: 0.72 },
      { source: "detritus", target: "fungi", weight: 0.84 },
    ],
    metadata: {},
  },
  null,
  2,
);

const defaultParameterSet = JSON.stringify(
  {
    name: "Baseline parameters",
    description: "Deterministic placeholder parameters.",
    parameters: {
      respirationRate: 0.12,
      decompositionRate: 0.08,
      turnoverRate: 0.05,
    },
    metadata: {},
  },
  null,
  2,
);

const defaultScenarioConfig = JSON.stringify(
  {
    horizonDays: 30,
    timeStepDays: 5,
  },
  null,
  2,
);

export function ScenarioCreateForm({ projectId }: { projectId: string }) {
  const router = useRouter();
  const [name, setName] = useState("Baseline scenario");
  const [description, setDescription] = useState("First deterministic placeholder scenario.");
  const [foodWebJson, setFoodWebJson] = useState(defaultFoodWeb);
  const [parameterSetJson, setParameterSetJson] = useState(defaultParameterSet);
  const [scenarioConfigJson, setScenarioConfigJson] = useState(defaultScenarioConfig);
  const [selectedSampleId, setSelectedSampleId] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const soilSamplesQuery = useSoilSamplesQuery(projectId);

  const defaultSampleId = useMemo(
    () => selectedSampleId || soilSamplesQuery.data?.items[0]?.id || "",
    [selectedSampleId, soilSamplesQuery.data?.items],
  );

  const createScenario = useCreateScenarioMutation(projectId, {
    onSuccess: () => {
      router.push(`/projects/${projectId}`);
    },
    onError: (error) => {
      setErrorMessage(getApiErrorMessage(error, "Failed to create scenario."));
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    createScenario.mutate({
      name: name.trim(),
      description: description.trim() || null,
      soilSampleId: defaultSampleId,
      foodWeb: parseJsonValue<ScenarioCreate["foodWeb"]>(foodWebJson),
      parameterSet: parseJsonValue<ScenarioCreate["parameterSet"]>(parameterSetJson),
      scenarioConfig: parseJsonObject(scenarioConfigJson, "Scenario config"),
    });
  }

  if (soilSamplesQuery.isLoading) {
    return <Panel className="text-[#5d624e]">Loading soil samples...</Panel>;
  }

  if (soilSamplesQuery.isError) {
    return (
      <Panel className="border-red-200 text-red-800">
        Failed to load soil samples.{" "}
        {soilSamplesQuery.error instanceof Error
          ? soilSamplesQuery.error.message
          : "Unknown error."}
      </Panel>
    );
  }

  if (!soilSamplesQuery.data?.items.length) {
    return (
      <Panel className="space-y-4">
        <PageHeader eyebrow="Scenario Setup" title="Add a soil sample first">
          The scenario requires a sample so the engine can build a complete input snapshot.
        </PageHeader>
        <Button onClick={() => router.push(`/projects/${projectId}/samples/new`)}>
          Create soil sample
        </Button>
      </Panel>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Scenario Setup" title="Create a simulation scenario">
        Define the biological network and parameter assumptions that the backend will version and
        pin to the selected soil sample.
      </PageHeader>

      <Panel className="space-y-6 p-8">
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="grid gap-6 md:grid-cols-[1.15fr_0.85fr]">
            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Scenario name</span>
              <Input
                onChange={(event: ChangeEvent<HTMLInputElement>) => setName(event.target.value)}
                value={name}
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Soil sample</span>
              <select
                className="w-full rounded-[18px] border border-[rgba(72,85,59,0.18)] bg-[#fffaf1] px-4 py-3 text-sm text-[#283422] outline-none"
                onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                  setSelectedSampleId(event.target.value)
                }
                value={defaultSampleId}
              >
                {soilSamplesQuery.data.items.map((soilSample) => (
                  <option key={soilSample.id} value={soilSample.id}>
                    {soilSample.sampleCode} - {soilSample.name || "Unnamed sample"}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="block space-y-2">
            <span className="text-sm font-semibold text-[#283422]">Description</span>
            <Textarea
              onChange={(event: ChangeEvent<HTMLTextAreaElement>) =>
                setDescription(event.target.value)
              }
              value={description}
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-semibold text-[#283422]">Food web JSON</span>
            <Textarea
              className="min-h-80 font-mono"
              onChange={(event: ChangeEvent<HTMLTextAreaElement>) =>
                setFoodWebJson(event.target.value)
              }
              value={foodWebJson}
            />
          </label>

          <div className="grid gap-6 lg:grid-cols-2">
            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Parameter set JSON</span>
              <Textarea
                className="min-h-56 font-mono"
                onChange={(event: ChangeEvent<HTMLTextAreaElement>) =>
                  setParameterSetJson(event.target.value)
                }
                value={parameterSetJson}
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Scenario config JSON</span>
              <Textarea
                className="min-h-56 font-mono"
                onChange={(event: ChangeEvent<HTMLTextAreaElement>) =>
                  setScenarioConfigJson(event.target.value)
                }
                value={scenarioConfigJson}
              />
            </label>
          </div>

          {errorMessage ? <p className="text-sm text-red-700">{errorMessage}</p> : null}

          <div className="flex flex-wrap items-center justify-between gap-4 rounded-[22px] bg-[rgba(255,255,255,0.45)] p-4">
            <p className="text-sm leading-6 text-[#5d624e]">
              This will create a versioned food web, a versioned parameter set, and a scenario
              pinned to the selected soil sample version.
            </p>
            <Button
              disabled={createScenario.isPending || defaultSampleId.length === 0}
              type="submit"
            >
              {createScenario.isPending ? "Creating..." : "Create scenario"}
            </Button>
          </div>
        </form>
      </Panel>
    </div>
  );
}

"use client";

import { useRouter } from "next/navigation";
import { ChangeEvent, FormEvent, useMemo, useState } from "react";

import { Button, Input, PageHeader, Panel, Textarea } from "@bio/ui";

import { useCreateSoilSampleMutation } from "../../hooks/use-bio-queries";
import { getApiErrorMessage } from "../../lib/api-errors";
import { parseJsonObject } from "../../lib/json";

export function SampleCreateForm({ projectId }: { projectId: string }) {
  const router = useRouter();
  const [sampleCode, setSampleCode] = useState("SAMPLE-001");
  const [name, setName] = useState("Baseline sample");
  const [description, setDescription] = useState("Initial soil sample for placeholder simulation.");
  const [collectedOn, setCollectedOn] = useState("");
  const [location, setLocation] = useState('{"field":"North Plot","depthCm":15}');
  const [measurements, setMeasurements] = useState(
    '{"organicMatter":4.2,"ph":6.8,"moisture":0.27}',
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const createSample = useCreateSoilSampleMutation(projectId, {
    onSuccess: () => {
      router.push(`/projects/${projectId}`);
    },
    onError: (error) => {
      setErrorMessage(getApiErrorMessage(error, "Failed to create soil sample."));
    },
  });

  const canSubmit = useMemo(() => sampleCode.trim().length > 0, [sampleCode]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    createSample.mutate({
      sampleCode: sampleCode.trim(),
      name: name.trim() || null,
      description: description.trim() || null,
      collectedOn: collectedOn || null,
      location: parseJsonObject(location, "Location"),
      measurements: parseJsonObject(measurements, "Measurements"),
      metadata: {},
    });
  }

  return (
    <div className="mx-auto max-w-[920px] space-y-8">
      <PageHeader eyebrow="Measured Inputs" title="Add a soil sample">
        Capture the measured sample that will anchor scenario assumptions and exact run provenance.
      </PageHeader>

      <Panel className="space-y-6 p-8">
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="grid gap-6 md:grid-cols-2">
            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Sample code</span>
              <Input
                onChange={(event: ChangeEvent<HTMLInputElement>) =>
                  setSampleCode(event.target.value)
                }
                value={sampleCode}
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Sample name</span>
              <Input
                onChange={(event: ChangeEvent<HTMLInputElement>) => setName(event.target.value)}
                value={name}
              />
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
            <span className="text-sm font-semibold text-[#283422]">Collected on</span>
            <Input
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                setCollectedOn(event.target.value)
              }
              type="date"
              value={collectedOn}
            />
          </label>

          <div className="grid gap-6 lg:grid-cols-2">
            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Location JSON</span>
              <Textarea
                className="min-h-56 font-mono"
                onChange={(event: ChangeEvent<HTMLTextAreaElement>) =>
                  setLocation(event.target.value)
                }
                value={location}
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Measurements JSON</span>
              <Textarea
                className="min-h-56 font-mono"
                onChange={(event: ChangeEvent<HTMLTextAreaElement>) =>
                  setMeasurements(event.target.value)
                }
                value={measurements}
              />
            </label>
          </div>

          {errorMessage ? <p className="text-sm text-red-700">{errorMessage}</p> : null}

          <div className="flex flex-wrap items-center justify-between gap-4 rounded-[22px] bg-[rgba(255,255,255,0.45)] p-4">
            <p className="text-sm leading-6 text-[#5d624e]">
              The backend will preserve a stable sample identity and create an immutable scientific
              version for this entry.
            </p>
            <Button disabled={createSample.isPending || !canSubmit} type="submit">
              {createSample.isPending ? "Saving..." : "Create soil sample"}
            </Button>
          </div>
        </form>
      </Panel>
    </div>
  );
}

"use client";

import { useRouter } from "next/navigation";
import { ChangeEvent, FormEvent, useMemo, useState } from "react";

import { Button, Input, PageHeader, Panel, Textarea } from "@bio/ui";

import { useCreateProjectMutation } from "../../hooks/use-bio-queries";
import { getApiErrorMessage } from "../../lib/api-errors";

export function ProjectCreateForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const suggestedSlug = useMemo(
    () =>
      name
        .toLowerCase()
        .trim()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "")
        .slice(0, 100),
    [name],
  );

  const createProject = useCreateProjectMutation({
    onSuccess: (project) => {
      router.push(`/projects/${project.id}`);
    },
    onError: (error) => {
      setErrorMessage(getApiErrorMessage(error, "Failed to create project."));
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    createProject.mutate({
      name: name.trim(),
      slug: slug.trim() || suggestedSlug || null,
      description: description.trim() || null,
      metadata: {},
    });
  }

  return (
    <div className="mx-auto max-w-[860px] space-y-8">
      <PageHeader eyebrow="Projects" title="Create a new soil project">
        Set up the workspace that will hold your measured samples, versioned scenarios, and run
        history for this site or client engagement.
      </PageHeader>

      <Panel className="space-y-6 p-8">
        <form className="space-y-6" onSubmit={handleSubmit}>
          <label className="block space-y-2">
            <span className="text-sm font-semibold text-[#283422]">Project name</span>
            <Input
              onChange={(event: ChangeEvent<HTMLInputElement>) => setName(event.target.value)}
              placeholder="North pasture regeneration program"
              value={name}
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-semibold text-[#283422]">Slug</span>
            <Input
              onChange={(event: ChangeEvent<HTMLInputElement>) => setSlug(event.target.value)}
              placeholder={suggestedSlug || "north-pasture-regeneration-program"}
              value={slug}
            />
            <p className="text-xs leading-6 text-[#7c7a67]">
              Optional. Leave blank to use an auto-generated slug from the project name.
            </p>
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-semibold text-[#283422]">Description</span>
            <Textarea
              onChange={(event: ChangeEvent<HTMLTextAreaElement>) =>
                setDescription(event.target.value)
              }
              placeholder="A project for collecting baseline soil biology measurements and testing scenario outcomes over time."
              value={description}
            />
          </label>

          {errorMessage ? <p className="text-sm text-red-700">{errorMessage}</p> : null}

          <div className="flex flex-wrap items-center justify-between gap-4 rounded-[22px] bg-[rgba(255,255,255,0.45)] p-4">
            <p className="text-sm leading-6 text-[#5d624e]">
              After creation, you can move directly into soil sample capture and scenario setup.
            </p>
            <Button disabled={createProject.isPending || name.trim().length < 3} type="submit">
              {createProject.isPending ? "Creating..." : "Create project"}
            </Button>
          </div>
        </form>
      </Panel>
    </div>
  );
}

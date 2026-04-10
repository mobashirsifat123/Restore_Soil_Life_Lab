"use client";

import Link from "next/link";

import { Button, Panel } from "@bio/ui";

import { useProjectsQuery } from "../../hooks/use-bio-queries";
import { getApiErrorMessage } from "../../lib/api-errors";

const dateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
});

export function ProjectsList({ mode = "page" }: { mode?: "dashboard" | "page" }) {
  const projectsQuery = useProjectsQuery();

  if (projectsQuery.isLoading) {
    return <Panel className="text-[#5d624e]">Loading projects...</Panel>;
  }

  if (projectsQuery.isError) {
    return (
      <Panel className="border-red-200 text-red-800">
        Failed to load projects. {getApiErrorMessage(projectsQuery.error, "Unknown error.")}
      </Panel>
    );
  }

  const items = projectsQuery.data?.items ?? [];
  const visibleItems = mode === "dashboard" ? items.slice(0, 4) : items;

  if (items.length === 0) {
    return (
      <Panel className="space-y-4">
        <div className="space-y-2">
          <p className="editorial-kicker font-mono text-xs">No current workspaces</p>
          <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
            Start the first project
          </h2>
          <p className="text-sm leading-6 text-[#5d624e]">
            Create a project to organize soil samples, scenarios, and worker-backed simulation runs.
          </p>
        </div>
        <Link href="/projects/new">
          <Button>Create your first project</Button>
        </Link>
      </Panel>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-2">
        {visibleItems.map((project) => (
          <Panel key={project.id} className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="font-serif text-[2rem] tracking-[-0.03em] text-[#283422]">
                    {project.name}
                  </h2>
                  <p className="font-mono text-caption uppercase tracking-[0.16em] text-[#7c7a67]">
                    {project.slug}
                  </p>
                </div>
                <span className="rounded-full bg-[rgba(85,99,71,0.1)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-[#556347]">
                  {project.status}
                </span>
              </div>
              <p className="text-sm leading-6 text-[#5d624e]">
                {project.description || "No project description has been added yet."}
              </p>
            </div>

            <div className="flex items-center justify-between gap-4 text-xs text-[#7c7a67]">
              <span>Created {dateFormatter.format(new Date(project.createdAt))}</span>
              <Link href={`/projects/${project.id}`}>
                <Button variant="secondary">Open Project</Button>
              </Link>
            </div>
          </Panel>
        ))}
      </div>

      {mode === "dashboard" && items.length > visibleItems.length ? (
        <div className="flex justify-end">
          <Link href="/projects">
            <Button variant="ghost">View all projects</Button>
          </Link>
        </div>
      ) : null}
    </div>
  );
}

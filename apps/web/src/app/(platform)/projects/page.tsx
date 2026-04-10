import { PageHeader } from "@bio/ui";

import { ProjectsList } from "../../../features/projects/projects-list";

export default function ProjectsPage() {
  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Projects" title="Project workspaces">
        Open an existing project or create a new one to manage soil samples, scenarios, and
        simulation runs.
      </PageHeader>
      <ProjectsList />
    </div>
  );
}

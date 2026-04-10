import { ScenarioCreateForm } from "../../../../../../features/scenarios/scenario-create-form";

export default async function ScenarioCreatePage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  return <ScenarioCreateForm projectId={projectId} />;
}

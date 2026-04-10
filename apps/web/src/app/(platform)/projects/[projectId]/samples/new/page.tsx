import { SampleCreateForm } from "../../../../../../features/samples/sample-create-form";

export default async function SampleCreatePage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  return <SampleCreateForm projectId={projectId} />;
}

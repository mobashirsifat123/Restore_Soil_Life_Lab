import { DashboardOverview } from "../../../features/dashboard/dashboard-overview";
import { getServerSession } from "../../../lib/server-session";

export default async function DashboardPage() {
  const session = await getServerSession();
  return <DashboardOverview session={session} />;
}

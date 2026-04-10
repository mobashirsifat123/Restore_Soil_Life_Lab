import type { PropsWithChildren } from "react";

import { MarketingShell } from "../../components/layout/marketing-shell";
import { getServerSession } from "../../lib/server-session";

export default async function MarketingLayout({ children }: PropsWithChildren) {
  const session = await getServerSession();

  return <MarketingShell initialSession={session}>{children}</MarketingShell>;
}

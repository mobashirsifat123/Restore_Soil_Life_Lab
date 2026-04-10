import { getServerSession } from "../../../lib/server-session";
import { getActiveFormula } from "../../../lib/cmsData";

import { SilkSoilClient } from "./silksoil-client";

export default async function SilkSoilPage() {
  const [session, activeFormula] = await Promise.all([getServerSession(), getActiveFormula()]);

  return (
    <SilkSoilClient
      userName={session?.user.fullName ?? session?.user.email ?? null}
      activeFormula={activeFormula}
    />
  );
}

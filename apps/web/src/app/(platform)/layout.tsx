import type { PropsWithChildren } from "react";

import { PlatformShell } from "../../components/layout/platform-shell";

export default function PlatformLayout({ children }: PropsWithChildren) {
  return <PlatformShell>{children}</PlatformShell>;
}

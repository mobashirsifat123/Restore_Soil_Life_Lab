import { redirect } from "next/navigation";

import { MemberSettings } from "../../../features/settings/member-settings";
import { getServerAuthSessions, getServerProfile } from "../../../lib/server-auth";
import { getServerSession } from "../../../lib/server-session";

export default async function SettingsPage() {
  const [session, initialProfile, initialSessions] = await Promise.all([
    getServerSession(),
    getServerProfile(),
    getServerAuthSessions(),
  ]);

  if (!session || !initialProfile) {
    redirect("/login");
  }

  return <MemberSettings initialProfile={initialProfile} initialSessions={initialSessions} />;
}

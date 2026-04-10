import Link from "next/link";

import { Panel } from "@bio/ui";

import { getServerSession } from "../../../lib/server-session";
import { SignOutButton } from "../../../components/auth/sign-out-button";

export async function SessionSummary() {
  const session = await getServerSession();

  if (!session) {
    return (
      <Panel className="space-y-3 p-4">
        <p className="editorial-kicker font-mono text-xs">Session</p>
        <p className="text-sm leading-6 text-[#5d624e]">
          You are not signed in to the member workspace yet.
        </p>
        <Link
          href="/login"
          className="inline-flex text-sm font-semibold text-[#3a5c2f] transition-colors hover:text-[#1e3318]"
        >
          Sign in
        </Link>
      </Panel>
    );
  }

  const isOrgAdmin = session.user.roles.includes("org_admin");
  const displayName = session.user.fullName ?? session.user.email;

  return (
    <Panel className="space-y-4 p-4">
      <div className="space-y-1">
        <p className="editorial-kicker font-mono text-xs">Signed in</p>
        <p className="text-sm font-semibold text-[#283422]">{displayName}</p>
        <p className="text-xs text-[#7c7a67]">{session.user.email}</p>
        <p className="text-xs text-[#7c7a67]">
          Organization {session.activeOrganizationId.slice(0, 8)}
        </p>
      </div>
      <div className="space-y-1">
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[#7c7a67]">Roles</p>
        <p className="text-sm leading-6 text-[#5d624e]">
          {session.user.roles.length ? session.user.roles.join(", ") : "No roles assigned"}
        </p>
      </div>
      <div className="flex flex-wrap gap-3">
        <Link
          href="/settings"
          className="inline-flex rounded-full border border-[rgba(58,92,47,0.14)] px-4 py-2 text-sm font-semibold text-[#1e3318] transition-colors hover:bg-white/80"
        >
          Account settings
        </Link>
        {isOrgAdmin ? (
          <Link
            href="/admin"
            className="inline-flex rounded-full bg-[#1e3318] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#31492a]"
          >
            Open Admin Panel
          </Link>
        ) : null}
        <SignOutButton
          redirectTo="/"
          label="Sign out"
          className="inline-flex rounded-full border border-[rgba(58,92,47,0.14)] px-4 py-2 text-sm font-semibold text-[#1e3318] transition-colors hover:bg-white/80"
        />
      </div>
    </Panel>
  );
}

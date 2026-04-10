import Link from "next/link";

import { Button, PageHeader, Panel } from "@bio/ui";
import type { SessionResponse } from "@bio/api-client";

export function DashboardOverview({ session }: { session: SessionResponse | null }) {
  const isOrgAdmin = Boolean(session?.user.roles.includes("org_admin"));
  const displayName = session?.user.fullName ?? session?.user.email;

  if (!session) {
    return (
      <div className="space-y-8">
        <PageHeader
          eyebrow="Member Access"
          title="Join the Bio Soil member workspace"
          actions={
            <div className="flex flex-wrap gap-3">
              <Link href="/login">
                <Button>Sign in</Button>
              </Link>
              <Link href="/login">
                <Button variant="secondary">Create account</Button>
              </Link>
            </div>
          }
        >
          Sign in to unlock SilkSoil, save your analysis work, and access the member-only soil
          restoration tools. This page is intentionally focused on membership access only.
        </PageHeader>

        <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
          <Panel className="space-y-4">
            <p className="editorial-kicker font-mono text-xs">What members get</p>
            <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
              SilkSoil first
            </h2>
            <ul className="space-y-3 text-sm leading-6 text-[#5d624e]">
              <li>1. Evaluate microbial condition and biological balance.</li>
              <li>2. See the most likely soil constraints affecting recovery.</li>
              <li>3. Get practical recommendations to improve soil quality.</li>
              <li>4. Return later with the same account and continue your work.</li>
            </ul>
          </Panel>

          <Panel className="space-y-4">
            <p className="editorial-kicker font-mono text-xs">Next step</p>
            <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
              Sign in to continue
            </h2>
            <p className="text-sm leading-7 text-[#5d624e]">
              If you already have an account, sign in and go directly into SilkSoil. If you are new,
              create your member account first.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/login">
                <Button>Open sign in</Button>
              </Link>
              <Link href="/silksoil">
                <Button variant="ghost">View SilkSoil overview</Button>
              </Link>
            </div>
          </Panel>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <PageHeader
        eyebrow="Member Workspace"
        title="Your member home"
        actions={
          <div className="flex flex-wrap gap-3">
            <Link href="/silksoil">
              <Button>Open SilkSoil</Button>
            </Link>
            <Link href="/settings">
              <Button variant="secondary">Account settings</Button>
            </Link>
            {isOrgAdmin ? (
              <Link href="/admin">
                <Button variant="ghost">Admin panel</Button>
              </Link>
            ) : null}
          </div>
        }
      >
        Welcome back, {displayName}. Start with SilkSoil to evaluate soil condition and get
        practical advice, then move into deeper scientific workflows only when you need them.
      </PageHeader>

      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <Panel className="space-y-5">
          <p className="editorial-kicker font-mono text-xs">Recommended next step</p>
          <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
            Run the SilkSoil analysis first
          </h2>
          <p className="text-sm leading-7 text-[#5d624e]">
            SilkSoil is the main member feature. It helps farmers understand microbial condition,
            food-web balance, and what to improve first before moving into advanced project work.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/silksoil">
              <Button>Open SilkSoil</Button>
            </Link>
            <Link href="/">
              <Button variant="ghost">Back to public home</Button>
            </Link>
          </div>
        </Panel>

        <div className="space-y-5">
          <Panel className="space-y-4">
            <p className="editorial-kicker font-mono text-xs">What you can do here</p>
            <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
              A cleaner member experience
            </h2>
            <ol className="space-y-4 text-sm leading-6 text-[#5d624e]">
              <li>1. Use SilkSoil immediately after sign-in.</li>
              <li>2. Review the score, microbial condition, and recommendations.</li>
              <li>3. Return to deeper research workflows only when needed.</li>
            </ol>
          </Panel>

          <Panel className="space-y-4">
            <p className="editorial-kicker font-mono text-xs">Advanced workflow</p>
            <p className="text-base leading-7 text-[#5d624e]">
              Projects, samples, scenarios, and runs are still available for deeper scientific work,
              but they no longer dominate the first member screen.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/projects" className="inline-flex">
                <Button variant="secondary">Open advanced workspace</Button>
              </Link>
              <Link href="/settings" className="inline-flex">
                <Button variant="ghost">Manage profile and security</Button>
              </Link>
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}

import Link from "next/link";

import { SignOutButton } from "../../components/auth/sign-out-button";
import { getServerSession } from "../../lib/server-session";
import { LoginClient } from "./login-client";

export default async function LoginPage() {
  const session = await getServerSession();
  const isOrgAdmin = Boolean(session?.user.roles.includes("org_admin"));

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-16 bg-[#f5efdf]">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-[rgba(58,92,47,0.08)] rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-[460px]">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <p className="font-serif text-[2.2rem] text-[#1e3318] leading-none mb-1">Bio Soil</p>
            <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[#5a7050]">
              Soil Food Web Institute
            </p>
          </Link>
        </div>

        {session ? (
          <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-8 shadow-xl">
            <div className="mb-7 text-center">
              <h1 className="font-serif text-2xl text-[#1e3318] mb-2">You are already signed in</h1>
              <p className="text-[#6a8060] text-sm">{session.user.email}</p>
            </div>

            <div className="rounded-2xl bg-[#f8f5ef] px-5 py-4 text-sm leading-6 text-[#5a7050]">
              Your browser already has a valid session. Continue to SilkSoil, open your member area,
              or sign out if you want to switch accounts.
            </div>

            <div className="mt-6 flex flex-col gap-3">
              <Link
                href="/silksoil"
                className="w-full rounded-full bg-[#3a5c2f] py-4 text-center font-semibold text-white transition-colors hover:bg-[#1e3318] shadow-md"
              >
                Open SilkSoil
              </Link>
              <Link
                href={isOrgAdmin ? "/admin" : "/dashboard"}
                className="w-full rounded-full border border-[rgba(58,92,47,0.18)] py-4 text-center font-semibold text-[#1e3318] transition-colors hover:bg-[rgba(58,92,47,0.06)]"
              >
                {isOrgAdmin ? "Open Admin Panel" : "Open Member Portal"}
              </Link>
              <SignOutButton
                redirectTo="/login"
                label="Sign out to use another account"
                className="w-full rounded-full border border-[rgba(191,75,62,0.18)] py-4 text-center font-semibold text-[#8e352b] transition-colors hover:bg-[rgba(191,75,62,0.06)]"
              />
            </div>
          </div>
        ) : (
          <LoginClient />
        )}

        {!session ? (
          <>
            <div className="mt-8 flex justify-center">
              <div className="rounded-full border border-[#d3ceb8] bg-[rgba(245,239,223,0.5)] px-4 py-2 text-[11px] font-medium text-[#7c7a67]">
                FastAPI now handles live sign-in and registration. Email recovery is still mocked in
                the UI pending mail delivery setup.
              </div>
            </div>

            <div className="mt-8 text-center">
              <Link
                href="/"
                className="text-xs font-semibold uppercase tracking-wider text-[#5a7050] hover:text-[#1e3318] transition-colors"
              >
                ← Return to Public Site
              </Link>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

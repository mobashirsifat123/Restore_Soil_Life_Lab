import Link from "next/link";

import { ResetPasswordClient } from "./reset-password-client";

type ResetPasswordPageProps = {
  searchParams: Promise<{
    token?: string;
  }>;
};

export default async function ResetPasswordPage({ searchParams }: ResetPasswordPageProps) {
  const params = await searchParams;

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

        <ResetPasswordClient initialToken={params.token ?? null} />
      </div>
    </div>
  );
}

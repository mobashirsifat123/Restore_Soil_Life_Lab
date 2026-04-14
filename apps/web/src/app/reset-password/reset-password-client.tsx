"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

type ErrorEnvelope = {
  error?: { message?: string };
  message?: string;
};

type ResetPasswordClientProps = {
  initialToken: string | null;
};

export function ResetPasswordClient({ initialToken }: ResetPasswordClientProps) {
  const token = initialToken;
  const [password, setPassword] = useState("");
  const [isHydrated, setIsHydrated] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  async function parseErrorMessage(response: Response, fallback: string) {
    try {
      const body = (await response.json()) as ErrorEnvelope;
      return body.error?.message ?? body.message ?? fallback;
    } catch {
      return fallback;
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await fetch("/api/bio/auth/reset-password", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          token,
          newPassword: password,
        }),
        credentials: "same-origin",
      });

      if (!response.ok) {
        setErrorMessage(await parseErrorMessage(response, "Password reset failed."));
        return;
      }

      setSuccessMessage("Password successfully reset. You can now sign in with your new password.");
      setPassword("");
    } catch {
      setErrorMessage("Password reset failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-8 shadow-xl">
        <div className="mb-7 text-center">
          <h1 className="font-serif text-2xl text-[#1e3318] mb-2">Invalid Reset Link</h1>
          <p className="text-[#6a8060] text-sm">
            This password reset link is missing a token or is no longer valid.
          </p>
        </div>

        <Link
          href="/login"
          className="block w-full rounded-full bg-[#3a5c2f] py-4 text-center font-semibold text-white transition-colors hover:bg-[#1e3318] shadow-md"
        >
          Return to Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-8 shadow-xl">
      <div aria-live="polite" className="sr-only">
        {errorMessage ?? successMessage ?? ""}
      </div>

      <div className="mb-7 text-center">
        <h1 className="font-serif text-2xl text-[#1e3318] mb-2">Choose a New Password</h1>
        <p className="text-[#6a8060] text-sm">
          Set a new password for your Bio Soil account.
        </p>
      </div>

      {successMessage ? (
        <>
          <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800 text-center">
            {successMessage}
          </div>

          <Link
            href="/login"
            className="mt-6 block w-full rounded-full bg-[#3a5c2f] py-4 text-center font-semibold text-white transition-colors hover:bg-[#1e3318] shadow-md"
          >
            Return to Sign In
          </Link>
        </>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="new-password"
              className="block text-xs font-semibold uppercase tracking-[0.1em] text-[#5a7050] mb-1.5"
            >
              New Password
            </label>
            <input
              id="new-password"
              type="password"
              required
              autoComplete="new-password"
              disabled={isSubmitting || !isHydrated}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 transition-all"
            />
            <p className="text-[10px] text-[#5a7050] mt-1.5 italic">
              Must be at least 8 characters with a number and symbol.
            </p>
          </div>

          {errorMessage && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              {errorMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting || !isHydrated}
            className="w-full rounded-full bg-[#3a5c2f] py-4 font-semibold text-white hover:bg-[#1e3318] disabled:opacity-70 transition-colors shadow-md"
          >
            {isSubmitting ? "Updating..." : isHydrated ? "Reset Password" : "Loading..."}
          </button>
        </form>
      )}
    </div>
  );
}

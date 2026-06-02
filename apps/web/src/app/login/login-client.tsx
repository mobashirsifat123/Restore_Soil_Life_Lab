"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

type ErrorEnvelope = {
  error?: { message?: string };
  message?: string;
  developmentResetUrl?: string | null;
};

type AuthState = "login" | "signup" | "forgot_password" | "email_sent";

export function LoginClient() {
  const [authState, setAuthState] = useState<AuthState>("login");
  const [name, setName] = useState("");
  const [organization, setOrganization] = useState("");
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [developmentResetUrl, setDevelopmentResetUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function parseErrorMessage(response: Response, fallback: string) {
    try {
      const body = (await response.json()) as ErrorEnvelope;
      return body.error?.message ?? body.message ?? fallback;
    } catch {
      return fallback;
    }
  }

  function resetFeedback() {
    setErrorMessage(null);
    setSuccessMessage(null);
  }

  function normalizeEmail(value: string) {
    return value.trim().toLowerCase();
  }
  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isSubmitting) {
      return;
    }
    setIsSubmitting(true);
    resetFeedback();

    try {
      const response = await fetch("/api/bio/auth/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email: normalizeEmail(email), password }),
        credentials: "same-origin",
      });

      if (!response.ok) {
        setErrorMessage(
          await parseErrorMessage(response, "Sign in failed. Ensure backend API is active."),
        );
        return;
      }

      window.location.assign("/dashboard");
    } catch {
      setErrorMessage("Sign in failed. Please check your connection and try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSignup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!agreeTerms) {
      setErrorMessage("You must agree to the Terms of Service to create an account.");
      return;
    }
    if (isSubmitting) {
      return;
    }
    setIsSubmitting(true);
    resetFeedback();

    try {
      const response = await fetch("/api/bio/auth/register", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          name: name.trim(),
          organizationName: organization.trim() || null,
          email: normalizeEmail(email),
          password,
        }),
        credentials: "same-origin",
      });

      if (!response.ok) {
        setErrorMessage(
          await parseErrorMessage(response, "Registration failed. Please check your information."),
        );
        return;
      }

      window.location.assign("/dashboard");
    } catch {
      setErrorMessage("Registration failed because the service is unavailable right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleForgotPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isSubmitting) {
      return;
    }
    setIsSubmitting(true);
    resetFeedback();

    try {
      const response = await fetch("/api/bio/auth/forgot-password", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email: normalizeEmail(email) }),
        credentials: "same-origin",
      });

      if (!response.ok) {
        setErrorMessage(await parseErrorMessage(response, "Could not start password reset."));
        return;
      }

      const body = (await response.json()) as ErrorEnvelope;
      setDevelopmentResetUrl(body.developmentResetUrl ?? null);
      setSuccessMessage(body.message ?? `If that account exists, a password reset link has been sent.`);
      setAuthState("email_sent");
    } catch {
      setErrorMessage("Could not start password reset. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const switchState = (newState: AuthState) => {
    setAuthState(newState);
    if (newState !== "email_sent") {
      setDevelopmentResetUrl(null);
    }
    resetFeedback();
  };

  return (
    <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-8 shadow-xl">
      <div aria-live="polite" className="sr-only">
        {errorMessage ?? successMessage ?? ""}
      </div>
      {authState === "login" && (
        <>
          <div className="mb-7 text-center">
            <h1 className="font-serif text-2xl text-[#1e3318] mb-2">Member Sign In</h1>
            <p className="text-[#6a8060] text-sm">Access SilkSoil and your scientific workspace.</p>
          </div>

          {successMessage && (
            <div className="mb-5 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800 text-center">
              {successMessage}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label
                htmlFor="login-email"
                className="block text-xs font-semibold uppercase tracking-[0.1em] text-[#5a7050] mb-1.5"
              >
                Email Address
              </label>
              <input
                id="login-email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 transition-all"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label
                  htmlFor="login-password"
                  className="block text-xs font-semibold uppercase tracking-[0.1em] text-[#5a7050]"
                >
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => switchState("forgot_password")}
                  className="text-xs font-semibold text-[#3a5c2f] hover:text-[#1e3318]"
                >
                  Forgot password?
                </button>
              </div>
              <input
                id="login-password"
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 transition-all"
              />
            </div>

            {errorMessage && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-full bg-[#3a5c2f] py-4 font-semibold text-white hover:bg-[#1e3318] disabled:opacity-70 transition-colors shadow-md mt-2"
            >
              {isSubmitting ? "Signing in..." : "Sign In to Workspace"}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-[#5a7050]">
            Don&apos;t have an account?{" "}
            <button
              onClick={() => switchState("signup")}
              className="font-semibold text-[#3a5c2f] hover:text-[#1e3318]"
            >
              Request Access
            </button>
          </p>
        </>
      )}

      {authState === "signup" && (
        <>
          <div className="mb-7 text-center">
            <h1 className="font-serif text-2xl text-[#1e3318] mb-2">Request Membership</h1>
            <p className="text-[#6a8060] text-sm">Join Bio Soil to access the SilkSoil tools.</p>
          </div>

          <form onSubmit={handleSignup} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="signup-name"
                  className="block text-xs font-semibold uppercase tracking-[0.1em] text-[#5a7050] mb-1.5"
                >
                  Full Name
                </label>
                <input
                  id="signup-name"
                  type="text"
                  required
                  autoComplete="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 transition-all"
                />
              </div>
              <div>
                <label
                  htmlFor="signup-organization"
                  className="block text-xs font-semibold uppercase tracking-[0.1em] text-[#5a7050] mb-1.5"
                >
                  Farm / Organization
                </label>
                <input
                  id="signup-organization"
                  type="text"
                  placeholder="Optional"
                  autoComplete="organization"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] px-4 py-3 text-[#1e3318] placeholder:text-[#5a7050]/50 focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 transition-all"
                />
              </div>
            </div>
            <div>
              <label
                htmlFor="signup-email"
                className="block text-xs font-semibold uppercase tracking-[0.1em] text-[#5a7050] mb-1.5"
              >
                Email Address
              </label>
              <input
                id="signup-email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 transition-all"
              />
            </div>
            <div>
              <label
                htmlFor="signup-password"
                className="block text-xs font-semibold uppercase tracking-[0.1em] text-[#5a7050] mb-1.5"
              >
                Create Password
              </label>
              <input
                id="signup-password"
                type="password"
                required
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 transition-all"
              />
              <p className="text-[10px] text-[#5a7050] mt-1.5 italic">
                Must be at least 8 characters with a number and symbol.
              </p>
            </div>

            <div className="flex items-start gap-3 py-2">
              <input
                type="checkbox"
                id="terms"
                required
                checked={agreeTerms}
                onChange={(e) => setAgreeTerms(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-[#8aaa7a] text-[#3a5c2f] focus:ring-[#3a5c2f]"
              />
              <label htmlFor="terms" className="text-xs text-[#5a7050] leading-snug">
                I agree to the{" "}
                <Link href="/terms" className="underline text-[#3a5c2f] hover:text-[#1e3318]">
                  Terms of Service
                </Link>{" "}
                and acknowledge the{" "}
                <Link href="/privacy" className="underline text-[#3a5c2f] hover:text-[#1e3318]">
                  Privacy Policy
                </Link>
                .
              </label>
            </div>

            {errorMessage && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting || !agreeTerms}
              className="w-full rounded-full bg-[#1e3318] py-4 font-semibold text-white hover:bg-[#3a5c2f] disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md mt-2"
            >
              {isSubmitting ? "Processing..." : "Create Account"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-[#5a7050]">
            Already have an account?{" "}
            <button
              onClick={() => switchState("login")}
              className="font-semibold text-[#3a5c2f] hover:text-[#1e3318]"
            >
              Sign In
            </button>
          </p>
        </>
      )}

      {authState === "forgot_password" && (
        <>
          <div className="mb-7 text-center">
            <div className="w-12 h-12 rounded-full border-2 border-[#e8e0cc] flex items-center justify-center text-xl mx-auto mb-4">
              🔐
            </div>
            <h1 className="font-serif text-2xl text-[#1e3318] mb-2">Reset Password</h1>
            <p className="text-[#6a8060] text-sm">
              Enter the email associated with your account and we&apos;ll send a password reset link.
            </p>
          </div>

          <form onSubmit={handleForgotPassword} className="space-y-4">
            <div>
              <label
                htmlFor="forgot-email"
                className="block text-xs font-semibold uppercase tracking-[0.1em] text-[#5a7050] mb-1.5"
              >
                Email Address
              </label>
              <input
                id="forgot-email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] px-4 py-3 text-[#1e3318] focus:ring-2 focus:ring-[#3a5c2f]/30"
              />
            </div>

            {errorMessage && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {errorMessage}
              </div>
            )}

            {successMessage && (
              <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
                {successMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-full bg-[#d4933d] py-4 font-semibold text-white hover:bg-[#b97849] disabled:opacity-70 transition-colors shadow-md mt-2"
            >
              {isSubmitting ? "Sending..." : "Send Reset Link"}
            </button>
          </form>

          <button
            onClick={() => switchState("login")}
            className="mt-6 w-full text-center text-sm font-semibold text-[#5a7050] hover:text-[#1e3318]"
          >
            ← Back to Sign In
          </button>
        </>
      )}

      {authState === "email_sent" && (
        <>
          <div className="mb-7 text-center">
            <div className="w-12 h-12 rounded-full bg-[#f0f7ed] flex items-center justify-center text-xl mx-auto mb-4">
              ✉️
            </div>
            <h1 className="font-serif text-2xl text-[#1e3318] mb-2">Check Your Email</h1>
            <p className="text-[#6a8060] text-sm">
              We&apos;ve sent a password reset link to{" "}
              <span className="font-semibold text-[#3a5c2f]">{email}</span>.
            </p>
          </div>

          {successMessage && (
            <div className="mb-5 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800 text-center">
              {successMessage}
            </div>
          )}

          {errorMessage && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 text-center">
              {errorMessage}
            </div>
          )}

          {developmentResetUrl ? (
            <a
              href={developmentResetUrl}
              className="mt-2 block w-full rounded-full bg-[#1e3318] py-4 text-center font-semibold text-white hover:bg-[#3a5c2f] transition-colors shadow-md"
            >
              Open Reset Page
            </a>
          ) : null}

          <button
            onClick={() => switchState("forgot_password")}
            className="mt-6 w-full text-center text-sm font-semibold text-[#5a7050] hover:text-[#1e3318]"
          >
            Resend Link
          </button>
        </>
      )}
    </div>
  );
}

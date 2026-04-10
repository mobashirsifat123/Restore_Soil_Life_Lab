"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useState, useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

import { ApiError, BioApiClient, type SessionResponse } from "@bio/api-client";
import { SignOutButton } from "../auth/sign-out-button";

const BioSilkChatWidget = dynamic(
  () => import("../chat/biosilk-chat-widget").then((module) => module.BioSilkChatWidget),
  {
    ssr: false,
  },
);

/* ─── Announcement Bar ─── */
function AnnouncementBar() {
  const [visible, setVisible] = useState(true);
  if (!visible) return null;
  return (
    <div className="relative bg-[#1e3318] py-2.5 text-center text-sm text-[#c8dbb8]">
      <span className="mr-2">🌱</span>
      <span>
        <strong className="text-white">New:</strong> SilkSoil — our member-exclusive soil analysis
        system — is now live.
      </span>
      <Link
        href="/silksoil"
        className="ml-3 underline underline-offset-2 text-[#a8cc8a] hover:text-white transition-colors"
      >
        Learn more →
      </Link>
      <button
        onClick={() => setVisible(false)}
        aria-label="Dismiss announcement"
        className="absolute right-4 top-1/2 -translate-y-1/2 text-[#7a9a6a] hover:text-white transition-colors text-lg leading-none"
      >
        ×
      </button>
    </div>
  );
}

type NavItemType = {
  href: string;
  label: string;
  exact: boolean;
  children?: { href: string; label: string }[];
};

const socialLinks = [
  { label: "Twitter", href: "https://x.com" },
  { label: "YouTube", href: "https://www.youtube.com" },
  { label: "LinkedIn", href: "https://www.linkedin.com" },
  { label: "Instagram", href: "https://www.instagram.com" },
] as const;

/* ─── Desktop Nav Item (supports dropdown) ─── */
function NavItem({ item, pathname }: { item: NavItemType; pathname: string }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const hasChildren = Array.isArray(item.children) && item.children.length > 0;
  const children = item.children ?? [];
  const isActive = item.exact
    ? pathname === item.href
    : item.href !== "/" && pathname.startsWith(item.href);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  if (!hasChildren) {
    return (
      <Link
        href={item.href}
        className={`px-3.5 py-2 text-[0.875rem] font-medium rounded-full transition-all duration-150 ${
          isActive
            ? "bg-white text-[#1e3318] shadow-sm"
            : "text-[#3d5035] hover:text-[#1e3318] hover:bg-white/70"
        }`}
      >
        {item.label}
      </Link>
    );
  }

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`flex items-center gap-1.5 px-3.5 py-2 text-[0.875rem] font-medium rounded-full transition-all duration-150 ${
          isActive
            ? "bg-white text-[#1e3318] shadow-sm"
            : "text-[#3d5035] hover:text-[#1e3318] hover:bg-white/70"
        }`}
      >
        {item.label}
        <svg
          className={`w-3.5 h-3.5 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="absolute left-0 top-full mt-2 min-w-[200px] rounded-2xl border border-[rgba(58,92,47,0.12)] bg-white/95 backdrop-blur-md shadow-xl py-2 z-50 animate-fade-in">
          {children.map((child) => (
            <Link
              key={child.href}
              href={child.href}
              onClick={() => setOpen(false)}
              className="block px-5 py-3 text-sm text-[#3d5035] hover:bg-[#f0f7ed] hover:text-[#1e3318] transition-colors"
            >
              {child.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

/* ─── Mobile Menu ─── */
function MobileMenu({
  open,
  onClose,
  session,
}: {
  open: boolean;
  onClose: () => void;
  session: { user: { email: string; fullName?: string | null; roles: string[] } } | null;
}) {
  const pathname = usePathname();
  const isOrgAdmin = Boolean(session?.user.roles.includes("org_admin"));
  const displayName = session?.user.fullName ?? session?.user.email;
  const navItems = [
    { href: "/", label: "Home" },
    { href: "/about", label: "About" },
    { href: "/silksoil", label: "🌱 SilkSoil" },
    { href: "/science", label: "Science" },
    { href: "/blog", label: "Blog" },
    { href: "/contact", label: "Contact Us" },
    ...(session
      ? [{ href: "/dashboard", label: "Member Portal" }]
      : [{ href: "/login", label: "Sign In" }]),
    ...(isOrgAdmin ? [{ href: "/admin", label: "Admin Panel" }] : []),
  ];

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        className={`fixed inset-0 bg-[#1a2214]/60 backdrop-blur-sm z-40 transition-opacity duration-300 ${open ? "opacity-100" : "opacity-0 pointer-events-none"}`}
      />
      {/* Slide-out panel */}
      <div
        id="mobile-nav-drawer"
        className={`fixed top-0 right-0 h-full w-[300px] bg-[#f5efdf] z-50 shadow-2xl transition-transform duration-300 ease-in-out flex flex-col ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-6 py-5 border-b border-[rgba(58,92,47,0.14)]">
          <span className="font-serif text-xl text-[#1e3318]">Bio Soil</span>
          <button
            onClick={onClose}
            aria-label="Close menu"
            className="text-[#5a7050] hover:text-[#1e3318] transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-1">
          {session ? (
            <div className="mb-4 rounded-xl bg-[rgba(58,92,47,0.08)] px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#5a7050]">
                Signed in
              </p>
              <p className="mt-1 text-sm font-semibold text-[#1e3318]">{displayName}</p>
            </div>
          ) : null}
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={`block px-4 py-3.5 rounded-xl text-base font-medium transition-colors ${
                pathname === item.href
                  ? "bg-[#1e3318] text-white"
                  : "text-[#3d5035] hover:bg-[rgba(58,92,47,0.08)] hover:text-[#1e3318]"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="px-4 py-6 border-t border-[rgba(58,92,47,0.14)]">
          <Link
            href={session ? "/silksoil" : "/login"}
            onClick={onClose}
            className="block w-full text-center bg-[#3a5c2f] text-white rounded-full py-3.5 font-semibold hover:bg-[#1e3318] transition-colors"
          >
            {session ? "Open SilkSoil" : "Sign In to Access SilkSoil"}
          </Link>
          {session ? (
            <SignOutButton
              redirectTo="/"
              label="Sign out"
              className="mt-3 block w-full rounded-full border border-[rgba(58,92,47,0.18)] py-3 text-sm font-semibold text-[#3d5035] transition-colors hover:bg-[rgba(58,92,47,0.08)] hover:text-[#1e3318]"
            />
          ) : null}
        </div>
      </div>
    </>
  );
}

/* ─── Main Marketing Shell ─── */
export function MarketingShell({
  children,
  initialSession,
}: {
  children: React.ReactNode;
  initialSession: SessionResponse | null;
}) {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [session, setSession] = useState<SessionResponse | null>(initialSession);
  const isOrgAdmin = Boolean(session?.user.roles.includes("org_admin"));
  const displayName = session?.user.fullName ?? session?.user.email;

  useEffect(() => {
    if (!initialSession) {
      setSession(null);
      return;
    }

    let active = true;
    const client = new BioApiClient({ baseUrl: "/api/bio" });

    async function refreshSession() {
      try {
        const nextSession = await client.getSession();
        if (active) {
          setSession(nextSession);
        }
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          if (active) {
            setSession(null);
          }
          return;
        }

        if (active) {
          setSession(initialSession);
        }
      }
    }

    refreshSession();

    return () => {
      active = false;
    };
  }, [initialSession, pathname]);

  const navItems: NavItemType[] = [
    { href: "/", label: "Home", exact: true },
    { href: "/about", label: "About", exact: true },
    { href: "/silksoil", label: "SilkSoil", exact: true },
    { href: "/science", label: "Science", exact: false },
    { href: "/blog", label: "Blog", exact: false },
    { href: "/contact", label: "Contact", exact: false },
  ];

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!mobileOpen) {
      return;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMobileOpen(false);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [mobileOpen]);

  return (
    <div className="min-h-screen bg-[#f5efdf]">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[1500] focus:rounded-full focus:bg-[#1e3318] focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
      >
        Skip to content
      </a>
      <AnnouncementBar />

      {/* ── Header ── */}
      <header
        className={`sticky top-0 z-[1200] transition-all duration-300 ${
          scrolled
            ? "premium-stroke bg-[linear-gradient(180deg,rgba(250,245,234,0.96),rgba(244,237,221,0.92))] backdrop-blur-md border-b border-[rgba(58,92,47,0.14)] shadow-sm"
            : "premium-stroke bg-[linear-gradient(180deg,rgba(248,242,231,0.9),rgba(244,237,221,0.84))] backdrop-blur border-b border-[rgba(58,92,47,0.10)]"
        }`}
      >
        <div className="mx-auto flex max-w-[1280px] items-center justify-between gap-6 px-6 py-3.5">
          {/* Logo */}
          <Link href="/" className="flex flex-col leading-none shrink-0">
            <span className="font-serif text-[1.65rem] text-[#1e3318] tracking-tight">
              Bio Soil
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[#5a7050] mt-0.5">
              Soil Food Web Institute
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1" aria-label="Main navigation">
            {navItems.map((item) => (
              <NavItem
                key={item.href}
                item={item as Parameters<typeof NavItem>[0]["item"]}
                pathname={pathname}
              />
            ))}
          </nav>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            {session ? (
              <>
                <div className="premium-stroke rounded-full border border-[rgba(58,92,47,0.14)] bg-white/80 px-4 py-2 text-right shadow-sm">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#5a7050]">
                    Signed in
                  </p>
                  <p className="text-sm font-semibold text-[#1e3318]">{displayName}</p>
                </div>
                {isOrgAdmin ? (
                  <Link
                    href="/admin"
                    className="rounded-full border border-[rgba(58,92,47,0.14)] px-5 py-2.5 text-sm font-semibold text-[#1e3318] hover:bg-white/80 transition-colors shadow-sm"
                  >
                    Admin
                  </Link>
                ) : null}
                <Link
                  href="/dashboard"
                  className="rounded-full bg-[#3a5c2f] px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#1e3318] transition-colors shadow-sm"
                >
                  Member Portal
                </Link>
                <SignOutButton
                  redirectTo="/"
                  label="Sign out"
                  className="rounded-full border border-[rgba(58,92,47,0.14)] px-5 py-2.5 text-sm font-semibold text-[#1e3318] hover:bg-white/80 transition-colors shadow-sm"
                />
              </>
            ) : (
              <Link
                href="/login"
                className="rounded-full bg-[#3a5c2f] px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#1e3318] transition-colors shadow-sm"
              >
                Sign In
              </Link>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            aria-label="Open menu"
            aria-expanded={mobileOpen}
            aria-controls="mobile-nav-drawer"
            className="md:hidden text-[#3d5035] hover:text-[#1e3318] transition-colors p-1"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </header>

      <MobileMenu open={mobileOpen} onClose={() => setMobileOpen(false)} session={session} />

      <main id="main-content">{children}</main>
      <BioSilkChatWidget initialSession={session} mode="floating" />

      {/* ── Footer ── */}
      <footer className="bg-[#1a2214] text-[#8aaa7a]">
        {/* Top CTA band */}
        <div className="bg-[radial-gradient(circle_at_top,rgba(138,210,179,0.12),transparent_24%),linear-gradient(180deg,#3d6131,#315126)] py-14 px-6 text-center">
          {session ? (
            <>
              <p className="editorial-kicker text-[#a8cc8a] mb-3">Welcome back</p>
              <h2 className="font-serif text-3xl md:text-4xl text-white mb-4 max-w-xl mx-auto leading-tight">
                Continue your soil analysis work
              </h2>
              <p className="text-[#b8d4a0] max-w-lg mx-auto mb-8 leading-relaxed">
                Your member account is active. Go straight into SilkSoil or return to your member
                home without seeing another sign-in prompt.
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <Link
                  href="/silksoil"
                  className="rounded-full bg-[#d4933d] px-7 py-3.5 font-semibold text-white hover:bg-[#b97849] transition-colors shadow-md"
                >
                  Open SilkSoil
                </Link>
                <Link
                  href="/dashboard"
                  className="rounded-full border border-white/30 px-7 py-3.5 font-semibold text-white hover:bg-white/10 transition-colors"
                >
                  Member Portal
                </Link>
              </div>
            </>
          ) : (
            <>
              <p className="editorial-kicker text-[#a8cc8a] mb-3">Join the movement</p>
              <h2 className="font-serif text-3xl md:text-4xl text-white mb-4 max-w-xl mx-auto leading-tight">
                Start Regenerating Soil Today
              </h2>
              <p className="text-[#b8d4a0] max-w-lg mx-auto mb-8 leading-relaxed">
                Sign in to access SilkSoil — our member-exclusive soil analysis system — and follow
                the science-backed path to soil restoration.
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <Link
                  href="/login"
                  className="rounded-full bg-[#d4933d] px-7 py-3.5 font-semibold text-white hover:bg-[#b97849] transition-colors shadow-md"
                >
                  Sign In to Access SilkSoil
                </Link>
                <Link
                  href="/about"
                  className="rounded-full border border-white/30 px-7 py-3.5 font-semibold text-white hover:bg-white/10 transition-colors"
                >
                  Learn the Science
                </Link>
              </div>
            </>
          )}
        </div>

        {/* Main footer columns */}
        <div className="mx-auto max-w-[1280px] px-6 py-14 grid grid-cols-2 md:grid-cols-4 gap-10">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <p className="font-serif text-2xl text-white mb-2">Bio Soil</p>
            <p className="text-xs uppercase tracking-[0.24em] text-[#6a8a5a] mb-4">
              Soil Food Web Institute
            </p>
            <p className="text-sm leading-7 text-[#7a9a6a] max-w-xs">
              Empowering farmers and consultants with science-backed soil biology tools, education,
              and a connected member platform.
            </p>
            <div className="flex gap-3 mt-6">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={social.label}
                  className="w-9 h-9 rounded-full border border-[#3a5035] flex items-center justify-center text-xs text-[#6a8a5a] hover:border-[#a8cc8a] hover:text-[#a8cc8a] transition-colors"
                >
                  {social.label[0]}
                </a>
              ))}
            </div>
          </div>

          {/* Services */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#a8cc8a] mb-5">
              Tools
            </p>
            <ul className="space-y-3 text-sm">
              {[
                ["SilkSoil Analysis", "/silksoil"],
                ["Sign In", "/login"],
              ].map(([label, href]) => (
                <li key={label}>
                  <Link href={href} className="hover:text-white transition-colors">
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Learn */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#a8cc8a] mb-5">
              Learn
            </p>
            <ul className="space-y-3 text-sm">
              {[
                ["How It Works", "/science"],
                ["About Us", "/about"],
                ["Blog & Updates", "/blog"],
                ["Case Studies", "/case-studies"],
                ["Contact Us", "/contact"],
              ].map(([label, href]) => (
                <li key={label}>
                  <Link href={href} className="hover:text-white transition-colors">
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal + Contact */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#a8cc8a] mb-5">
              Company
            </p>
            <ul className="space-y-3 text-sm">
              {[
                ["Privacy Policy", "/privacy"],
                ["Terms & Conditions", "/terms"],
                ["Cookie Policy", "/cookies"],
              ].map(([label, href]) => (
                <li key={label}>
                  <Link href={href} className="hover:text-white transition-colors">
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
            <div className="mt-6 text-sm leading-6">
              <p className="text-[#a8cc8a] font-medium mb-1">Contact</p>
              <a
                href="mailto:info@biosoil.com"
                className="hover:text-white transition-colors block"
              >
                info@biosoil.com
              </a>
              <p className="mt-1 text-[#6a8a5a]">Corvallis, OR 97330</p>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-[#2a3a22] px-6 py-5 text-center text-xs text-[#5a7050]">
          © {new Date().getFullYear()} Bio Soil — Soil Food Web Institute. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

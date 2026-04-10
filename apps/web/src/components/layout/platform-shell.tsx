import Link from "next/link";
import type { PropsWithChildren } from "react";

import { platformNavigation } from "../../lib/navigation";
import { getServerSession } from "../../lib/server-session";
import { SessionSummary } from "../../features/auth/components/session-summary";
import { NavLink } from "../navigation/nav-link";

export async function PlatformShell({ children }: PropsWithChildren) {
  const session = await getServerSession();
  const baseNavigationItems = session
    ? platformNavigation
    : platformNavigation.filter((item) => item.href !== "/settings");
  const navigationItems = session?.user.roles.includes("org_admin")
    ? [...baseNavigationItems, { href: "/admin", label: "Admin", exact: false }]
    : baseNavigationItems;

  return (
    <div className="min-h-screen bg-platform-grid">
      <a
        href="#platform-main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-[#1e3318] focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
      >
        Skip to main content
      </a>
      <header className="premium-stroke sticky top-0 z-20 border-b border-[rgba(58,92,47,0.14)] bg-[linear-gradient(180deg,rgba(250,245,234,0.96),rgba(244,237,221,0.92))] backdrop-blur-md shadow-sm">
        <div className="mx-auto flex max-w-[1380px] items-center justify-between gap-6 px-6 py-3.5">
          {/* Logo */}
          <Link href="/" className="flex flex-col leading-none shrink-0">
            <span className="font-serif text-[1.65rem] text-[#1e3318] tracking-tight">
              Bio Soil
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[#5a7050] mt-0.5">
              Member Portal
            </span>
          </Link>

          <nav className="hidden items-center gap-2 lg:flex" aria-label="Member navigation">
            {navigationItems.map((item) => (
              <NavLink
                key={`${item.href}-${item.label}`}
                exact={item.exact}
                href={item.href}
                label={item.label}
                variant="platform"
              />
            ))}
          </nav>
        </div>

        <div className="border-t border-[rgba(58,92,47,0.1)] px-4 py-3 lg:hidden">
          <nav
            aria-label="Member navigation mobile"
            className="mx-auto flex max-w-[1380px] gap-2 overflow-x-auto pb-1"
          >
            {navigationItems.map((item) => (
              <NavLink
                key={`${item.href}-${item.label}-mobile`}
                exact={item.exact}
                href={item.href}
                label={item.label}
                variant="platform"
              />
            ))}
          </nav>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1380px] gap-8 px-6 py-8 lg:grid-cols-[280px_minmax(0,1fr)]">
        {/* Sidebar */}
        <aside className="space-y-4">
          <SessionSummary />

          {/* SilkSoil quick-link */}
          <div className="glass-panel rounded-2xl p-5 text-white">
            <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-[#a8cc8a] mb-2">
              Member Tool
            </p>
            <p className="font-serif text-xl mb-1">SilkSoil</p>
            <p className="text-xs text-[#8aaa7a] leading-5 mb-4">
              SILK Soil Analysis System — run your full soil health score with 10 biological and
              chemical indicators.
            </p>
            <Link
              href="/silksoil"
              className="block text-center rounded-full bg-[#3a5c2f] py-2.5 text-sm font-semibold text-white hover:bg-[#4e7a40] transition-colors"
            >
              Open SilkSoil
            </Link>
          </div>

          <div className="premium-stroke rounded-2xl border border-[rgba(58,92,47,0.14)] bg-white/70 p-5 text-sm text-[#5d624e]">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#5a7050] mb-2">
              Navigation
            </p>
            <Link
              href="/"
              className="font-semibold text-[#3a5c2f] hover:text-[#1e3318] transition-colors text-sm"
            >
              ← Return to Public Site
            </Link>
          </div>
        </aside>

        <main id="platform-main" className="space-y-8">
          {children}
        </main>
      </div>
    </div>
  );
}

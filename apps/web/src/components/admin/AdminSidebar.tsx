"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const navItems = [
  { href: "/admin", label: "Dashboard", icon: "⊞", exact: true },
  { href: "/admin/home", label: "Homepage", icon: "🏠" },
  { href: "/admin/about", label: "About Page", icon: "👥" },
  { href: "/admin/science", label: "Science Page", icon: "🔬" },
  { href: "/admin/blog", label: "Blog & Posts", icon: "📝" },
  { href: "/admin/calculator", label: "Calculator Formula", icon: "📊" },
  { href: "/admin/media", label: "Media Library", icon: "🖼️" },
  { href: "/admin/chat", label: "BioSilk Chat", icon: "💬" },
  { href: "/admin/users", label: "Users", icon: "🙍" },
  { href: "/admin/user-log", label: "User Log", icon: "🕘" },
];

export function AdminSidebar() {
  const pathname = usePathname();
  const [loggingOut, setLoggingOut] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!mobileOpen) {
      return;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [mobileOpen]);

  async function handleLogout() {
    setLoggingOut(true);
    await fetch("/api/bio/auth/logout", { method: "POST", credentials: "same-origin" });
    window.location.assign("/login");
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setMobileOpen((current) => !current)}
        className="fixed left-4 top-4 z-[70] inline-flex h-11 w-11 items-center justify-center rounded-full border border-[rgba(168,204,138,0.18)] bg-[rgba(15,28,10,0.92)] text-white shadow-lg backdrop-blur md:hidden"
        aria-label={mobileOpen ? "Close admin navigation" : "Open admin navigation"}
        aria-expanded={mobileOpen}
      >
        {mobileOpen ? "×" : "≡"}
      </button>
      {mobileOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-[rgba(5,10,4,0.66)] md:hidden"
          aria-label="Close navigation overlay"
          onClick={() => setMobileOpen(false)}
        />
      ) : null}
      <aside
        className={`fixed bottom-0 left-0 top-0 z-50 flex w-72 flex-col border-r border-[rgba(168,204,138,0.1)] bg-[#0f1c0a] transition-transform duration-300 md:w-64 ${mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}
      >
        {/* Logo */}
        <div className="border-b border-[rgba(168,204,138,0.1)] p-6 pt-16 md:pt-6">
          <Link href="/" target="_blank" className="block">
            <p className="font-serif text-xl text-white leading-none">Bio Soil</p>
            <p className="text-[10px] font-semibold uppercase tracking-[0.25em] text-[#5a8050] mt-0.5">
              Admin Panel
            </p>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          {navItems.map((item) => {
            const isActive = item.exact ? pathname === item.href : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-5 py-3 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-[rgba(58,92,47,0.4)] text-white border-r-2 border-[#a8cc8a]"
                    : "text-[#7a9a6a] hover:text-white hover:bg-[rgba(58,92,47,0.2)]"
                }`}
              >
                <span className="text-base">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-[rgba(168,204,138,0.1)] p-4">
          <a
            href="/"
            target="_blank"
            className="flex items-center gap-2 text-xs text-[#5a7050] hover:text-[#a8cc8a] transition-colors mb-3"
          >
            <span>↗</span> View live site
          </a>
          <button
            onClick={handleLogout}
            disabled={loggingOut}
            className="w-full text-left text-xs text-[#5a7050] hover:text-red-400 transition-colors disabled:opacity-50"
          >
            {loggingOut ? "Signing out..." : "⏻ Sign out"}
          </button>
        </div>
      </aside>
    </>
  );
}

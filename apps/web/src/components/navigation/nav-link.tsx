"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "../../lib/cn";

type NavLinkVariant = "marketing" | "platform";

export function NavLink({
  href,
  label,
  exact = false,
  variant = "platform",
}: {
  href: string;
  label: string;
  exact?: boolean;
  variant?: NavLinkVariant;
}) {
  const pathname = usePathname();
  const isActive = exact ? pathname === href : pathname === href || pathname.startsWith(`${href}/`);

  return (
    <Link
      className={cn(
        "rounded-full px-3 py-2 text-sm font-medium transition-colors duration-base",
        variant === "marketing" && "text-mineral-700 hover:bg-white/80 hover:text-ink-950",
        variant === "platform" && "text-mineral-700 hover:bg-mineral-100 hover:text-ink-950",
        isActive &&
          (variant === "marketing"
            ? "bg-white text-ink-950 shadow-flat"
            : "bg-white text-ink-950 shadow-flat"),
      )}
      href={href}
    >
      {label}
    </Link>
  );
}

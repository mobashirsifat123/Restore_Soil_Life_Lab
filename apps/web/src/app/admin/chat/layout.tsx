"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { href: "/admin/chat", label: "Overview", exact: true },
  { href: "/admin/chat/prompt-lab", label: "Prompt Lab" },
  { href: "/admin/chat/sources", label: "Knowledge Sources" },
  { href: "/admin/chat/tools", label: "Tools" },
  { href: "/admin/chat/analytics", label: "Analytics" },
];

export default function AdminChatLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="max-w-[1200px] py-10 px-8">
      <div className="mb-8">
        <h1 className="font-serif text-3xl font-bold text-[#1e3318] mb-2">
          BioSilk Chat Management
        </h1>
        <p className="text-[#5a7050]">
          Configure the assistant, manage prompts, tools, and evaluate logs.
        </p>
      </div>

      <div className="border-b border-[rgba(58,92,47,0.12)] mb-8 flex gap-6">
        {tabs.map((tab) => {
          const isActive = tab.exact ? pathname === tab.href : pathname.startsWith(tab.href);
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={`pb-3 text-sm font-semibold transition-colors border-b-2 ${
                isActive
                  ? "text-[#1e3318] border-[#3a5c2f]"
                  : "text-[#7a9a6a] border-transparent hover:text-[#3a5c2f] hover:border-[rgba(58,92,47,0.2)]"
              }`}
            >
              {tab.label}
            </Link>
          );
        })}
      </div>

      <main>{children}</main>
    </div>
  );
}

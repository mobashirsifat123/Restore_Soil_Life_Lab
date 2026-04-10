import Link from "next/link";

const sections = [
  {
    href: "/admin/home",
    label: "Homepage",
    icon: "🏠",
    desc: "Hero heading, problem cards, stats, testimonials, calculator spotlight",
  },
  {
    href: "/admin/about",
    label: "About Page",
    icon: "👥",
    desc: "Mission text, team members, milestones, stats",
  },
  {
    href: "/admin/science",
    label: "Science Page",
    icon: "🔬",
    desc: "Food web levels, key concept cards, scientific stats",
  },
  {
    href: "/admin/blog",
    label: "Blog & Posts",
    icon: "📝",
    desc: "Create, edit, publish and delete blog articles",
  },
  {
    href: "/admin/calculator",
    label: "Calculator Formula",
    icon: "📊",
    desc: "SilkSoil scoring weights, thresholds and score bands",
  },
  {
    href: "/admin/media",
    label: "Media Library",
    icon: "🖼️",
    desc: "Upload and manage images used across the site",
  },
  {
    href: "/admin/users",
    label: "Users",
    icon: "🙍",
    desc: "See all registered members and their organization access",
  },
  {
    href: "/admin/user-log",
    label: "User Log",
    icon: "🕘",
    desc: "See recent sign-ins, sign-ups, and workflow activity",
  },
];

export default function AdminDashboard() {
  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-10">
        <p className="text-[#5a8050] text-xs font-semibold uppercase tracking-[0.2em] mb-2">
          Bio Soil
        </p>
        <h1 className="font-serif text-4xl text-white mb-3">Content Manager</h1>
        <p className="text-[#5a7a50] leading-7">
          Manage every piece of content on your site from here. Changes go live within 60 seconds
          via ISR caching.
        </p>
      </div>

      {/* Quick links */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5 mb-10">
        {sections.map((s) => (
          <Link
            key={s.href}
            href={s.href}
            className="group rounded-2xl border border-[rgba(168,204,138,0.1)] bg-[rgba(255,255,255,0.03)] p-6 hover:bg-[rgba(58,92,47,0.2)] hover:border-[rgba(168,204,138,0.25)] transition-all"
          >
            <span className="text-3xl block mb-4">{s.icon}</span>
            <h2 className="font-serif text-lg text-white mb-2 group-hover:text-[#a8cc8a] transition-colors">
              {s.label}
            </h2>
            <p className="text-sm text-[#5a7050] leading-6">{s.desc}</p>
            <span className="mt-4 inline-block text-xs font-semibold text-[#3a6030] group-hover:text-[#a8cc8a] transition-colors">
              Edit →
            </span>
          </Link>
        ))}
      </div>

      {/* Tips */}
      <div className="rounded-2xl border border-[rgba(168,204,138,0.08)] bg-[rgba(58,92,47,0.1)] p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-3">
          How it works
        </p>
        <div className="grid md:grid-cols-3 gap-4 text-sm text-[#5a7050]">
          <div>
            <p className="font-semibold text-[#8aaa7a] mb-1">✏️ Edit content</p>
            <p className="leading-6">
              Use the section editors to update text, images, cards, and lists for any page.
            </p>
          </div>
          <div>
            <p className="font-semibold text-[#8aaa7a] mb-1">💾 Save changes</p>
            <p className="leading-6">Hit Save — changes are stored in Supabase immediately.</p>
          </div>
          <div>
            <p className="font-semibold text-[#8aaa7a] mb-1">⚡ Goes live fast</p>
            <p className="leading-6">
              The public site refreshes via ISR caching within 60 seconds.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

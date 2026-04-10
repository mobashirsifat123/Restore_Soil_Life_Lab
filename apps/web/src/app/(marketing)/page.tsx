import Link from "next/link";
import Image from "next/image";
import { getCmsPage, getFeaturedPosts } from "@/lib/cmsData";
import { getServerSession } from "@/lib/server-session";
import type { SessionResponse } from "@bio/api-client";
import type {
  BlogPostSummary,
  CmsPage,
  HomeProblem,
  HomeSections,
  HomeStat,
  Testimonial,
} from "@/lib/cmsTypes";

export const revalidate = 60; // ISR — rebuild from DB every 60s

/* ── Server-side data fetch ── */
async function getHomeData() {
  try {
    const [pageData, featuredPosts] = await Promise.all([getCmsPage("home"), getFeaturedPosts()]);
    return { pageData, featuredPosts: featuredPosts ?? [] };
  } catch {
    return { pageData: null, featuredPosts: [] };
  }
}

/* ── Fallback data (used if API is down) ── */
const FALLBACK_PROBLEMS = [
  {
    title: "Diminishing Soil Fertility",
    subtitle: "The Soil-ution",
    body: "With a restored soil food web in place, plants can control nutrient cycling in their root zones.",
    icon: "🌿",
    link: "/science/nutrient-cycling",
  },
  {
    title: "Diseases, Pests & Weeds",
    subtitle: "Problem Solved",
    body: "The soil food web provides natural protection against pests and diseases.",
    icon: "🛡️",
    link: "/science",
  },
  {
    title: "Declining Farm Profits",
    subtitle: "How We Help",
    body: "When the soil food web is restored, farmers no longer need chemicals.",
    icon: "📈",
    link: "/science",
  },
  {
    title: "Climate Change",
    subtitle: "Carbon Sequestration",
    body: "Plants absorb carbon and invest ~40% into the soil to feed microorganisms.",
    icon: "🌍",
    link: "/science/carbon-sequestration",
  },
  {
    title: "Bird & Insect Decline",
    subtitle: "Ecosystem Restoration",
    body: "With the soil food web in place, the entire ecosystem flourishes.",
    icon: "🦋",
    link: "/science",
  },
  {
    title: "Soil Erosion",
    subtitle: "Structure Formation",
    body: "Soil food web microorganisms build soil structure that prevents erosion.",
    icon: "⛰️",
    link: "/science",
  },
];
const FALLBACK_STATS = [
  { number: "150%", label: "Reported yield increase", sub: "In the first growing season" },
  { number: "100%", label: "Reduction in pest damage", sub: "Using natural food web protection" },
  { number: "60%", label: "Cut in fertilizer costs", sub: "After soil biology restored" },
  { number: "6", label: "Continents with proven results", sub: "Farmers transformed worldwide" },
];
const FALLBACK_TESTIMONIALS = [
  {
    quote:
      "Our farm was in serious trouble, but after implementing the soil food web approach we increased our yield by 150% in a single season.",
    author: "Hassan A.",
    role: "Grain Farmer, Morocco",
  },
  {
    quote: "I'm learning so much I never knew before. Bio Soil explains everything so precisely.",
    author: "Meredith L.",
    role: "Horticulturist, New Zealand",
  },
  {
    quote: "It was one of the greatest courses I have ever taken.",
    author: "Thomas B.",
    role: "Agricultural Consultant, Germany",
  },
  {
    quote: "Great information. The soil health calculator alone saved me weeks of guesswork.",
    author: "Sara M.",
    role: "Regenerative Farmer, Oregon",
  },
  {
    quote: "Obviously the content is invaluable.",
    author: "Akira T.",
    role: "Soil Scientist, Japan",
  },
  {
    quote: "It has filled in gaps in my knowledge on how to heal depleted soil.",
    author: "Camille R.",
    role: "Permaculture Designer, France",
  },
];

/* ── Hero Section ── */
function Hero({ page, stats }: { page: CmsPage | undefined; stats: HomeStat[] }) {
  // We keep session for potential future checks or let it stay unused if not strictly linted

  const signalPills = ["Biology", "Moisture", "Carbon", "Field Signals"];

  return (
    <section className="bg-hero futuristic-grid relative flex min-h-[92vh] items-center overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="ambient-float ambient-pulse absolute left-[6%] top-[14%] h-[420px] w-[420px] rounded-full bg-[rgba(212,147,61,0.12)] blur-3xl" />
        <div className="ambient-float-delayed absolute right-[8%] top-[18%] h-[300px] w-[300px] rounded-full bg-[rgba(109,187,151,0.14)] blur-3xl" />
        <div className="ambient-float absolute bottom-[-30px] right-[16%] h-[360px] w-[360px] rounded-full bg-[rgba(58,92,47,0.18)] blur-3xl" />
      </div>

      <div className="relative mx-auto grid w-full max-w-[1280px] gap-16 px-6 py-24 lg:grid-cols-[minmax(0,760px)_minmax(360px,1fr)] lg:items-center">
        <div className="max-w-[760px]">
          <div className="mb-6 flex flex-wrap gap-3 reveal-rise">
            {signalPills.map((pill) => (
              <span key={pill} className="signal-pill hero-diamond-pill diamond-sheen">
                {pill}
              </span>
            ))}
          </div>
          <p className="editorial-kicker mb-5 text-[#a8cc8a] reveal-rise reveal-rise-delay-1">
            {page?.hero_kicker ?? "Soil Food Web Science · Education · Precision Tools"}
          </p>
          <h1 className="mb-7 font-serif text-[3.5rem] leading-[0.9] tracking-[-0.05em] text-white reveal-rise reveal-rise-delay-1 md:text-[5.35rem]">
            {page?.hero_heading ??
              "Healthy soil starts with understanding the living community beneath your feet."}
          </h1>
          <p className="mb-10 max-w-[640px] text-[1.15rem] leading-8 text-[#c0d8a8] reveal-rise reveal-rise-delay-2">
            {page?.hero_subheading ??
              "Bio Soil brings together soil biology education, a free soil health calculator, and a scientific member platform."}
          </p>
          <div className="flex flex-wrap gap-4 reveal-rise reveal-rise-delay-2">
            <Link
              href="/chat"
              className="button-glow rounded-full bg-[#d4933d] px-7 py-4 text-base font-semibold text-white shadow-lg transition-colors hover:bg-[#b97849]"
            >
              Open BioSilk Chat
            </Link>
            <Link
              href="/science"
              className="button-glow hero-diamond-button diamond-sheen rounded-full border px-7 py-4 text-base font-semibold text-white transition-colors"
            >
              Explore the science
            </Link>
          </div>
          <div className="mt-12 grid grid-cols-2 gap-4 md:grid-cols-4">
            {stats.slice(0, 4).map((stat) => (
              <div
                key={stat.number}
                className="hero-stat-card reveal-rise diamond-sheen rounded-2xl border border-white/12 px-5 py-5"
              >
                <p className="font-serif text-[2.4rem] font-bold leading-none text-[#d4933d]">
                  {stat.number}
                </p>
                <p className="mt-2 text-sm font-medium leading-5 text-white">{stat.label}</p>
                <p className="mt-1 text-xs text-[#8aaa7a]">{stat.sub}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative hidden lg:block">
          <div className="glass-panel hero-diamond-panel surface-sheen reveal-rise reveal-rise-delay-3 relative overflow-hidden rounded-[34px] p-6 text-white">
            <div className="absolute right-5 top-5 flex gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-[rgba(255,255,255,0.18)]" />
              <span className="h-2.5 w-2.5 rounded-full bg-[rgba(255,255,255,0.18)]" />
              <span className="h-2.5 w-2.5 rounded-full bg-[rgba(255,255,255,0.18)]" />
            </div>
            <div className="panel-orbit left-[14%] top-[14%] h-[260px] w-[260px]" />
            <div className="panel-orbit panel-orbit-reverse bottom-[12%] right-[10%] h-[180px] w-[180px]" />

            <div className="relative z-10 space-y-6">
              <div>
                <p className="panel-label">Field Intelligence Layer</p>
                <h3 className="mt-3 max-w-[320px] font-serif text-[2rem] leading-tight tracking-[-0.03em] text-white">
                  Read the hidden patterns shaping soil performance.
                </h3>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="panel-stat">
                  <p className="panel-label">Biological Activity</p>
                  <p className="mt-3 font-serif text-[2.2rem] leading-none text-[#d4933d]">84</p>
                  <p className="mt-2 text-sm text-[#cbdcc4]">Active microbial profile</p>
                </div>
                <div className="panel-stat">
                  <p className="panel-label">Water Logic</p>
                  <p className="mt-3 font-serif text-[2.2rem] leading-none text-[#8ad2b3]">+28%</p>
                  <p className="mt-2 text-sm text-[#cbdcc4]">Retention upside</p>
                </div>
              </div>

              <div className="rounded-[26px] border border-[rgba(215,230,207,0.12)] bg-[rgba(245,249,240,0.05)] p-5">
                <div className="flex items-center justify-between">
                  <p className="panel-label">Restoration Signals</p>
                  <span className="rounded-full bg-[rgba(138,210,179,0.14)] px-3 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-[#bde5d3]">
                    Stable
                  </span>
                </div>
                <div className="mt-5 space-y-4">
                  {[
                    { label: "Fungal balance", value: "72%" },
                    { label: "Carbon capture capacity", value: "68%" },
                    { label: "Root-zone resilience", value: "81%" },
                  ].map((item) => (
                    <div key={item.label}>
                      <div className="mb-2 flex items-center justify-between text-sm text-[#d9e6d2]">
                        <span>{item.label}</span>
                        <span>{item.value}</span>
                      </div>
                      <div className="h-2 rounded-full bg-[rgba(255,255,255,0.08)]">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-[#8ad2b3] via-[#b5d487] to-[#d4933d]"
                          style={{ width: item.value }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ── Problems Section ── */
function ProblemsSection({ problems }: { problems: HomeProblem[] }) {
  return (
    <section className="content-auto bg-[#f5efdf] px-6 py-24">
      <div className="mx-auto max-w-[1280px]">
        <div className="mb-14 grid gap-8 lg:grid-cols-[minmax(0,1.3fr)_minmax(320px,0.7fr)] lg:items-end">
          <div className="section-frame max-w-3xl">
            <p className="editorial-kicker mb-3 text-[#3a5c2f]">Why the soil food web matters</p>
            <h2 className="mb-4 font-serif text-[2.6rem] leading-tight tracking-[-0.03em] text-[#1e3318] md:text-[3.4rem]">
              Agriculture faces serious threats. The soil is the solution.
            </h2>
            <p className="text-lg leading-8 text-[#4a5e40]">
              Modern farming has degraded the biological communities living in soil, causing
              cascading problems. Restoring the soil food web addresses all of them.
            </p>
          </div>

          <div className="paper-tech-card rounded-[30px] p-6">
            <div className="relative z-10">
              <span className="signal-chip-light">System Scan</span>
              <p className="mt-5 font-serif text-[1.55rem] leading-snug text-[#1f2c18]">
                One biological foundation can improve six pressure points across the farm.
              </p>
              <p className="mt-3 text-sm leading-7 text-[#55644c]">
                Fertility, pest pressure, erosion, water logic, carbon, and profitability all move
                when the living soil network starts functioning again.
              </p>
            </div>
          </div>
        </div>

        <div className="stagger grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {problems.map((problem, index) => (
            <Link key={problem.title} href={problem.link} className="group">
              <div className="paper-tech-card card-hover h-full rounded-3xl p-7">
                <div className="relative z-10 flex h-full flex-col">
                  <div className="mb-5 flex items-start justify-between gap-4">
                    <span className="text-3xl">{problem.icon}</span>
                    <span className="signal-chip-light">0{index + 1}</span>
                  </div>
                  <p className="editorial-kicker mb-1 text-[#3a5c2f]">{problem.subtitle}</p>
                  <h3 className="mb-3 font-serif text-[1.45rem] leading-snug text-[#1e3318] transition-colors group-hover:text-[#3a5c2f]">
                    {problem.title}
                  </h3>
                  <p className="flex-1 text-sm leading-7 text-[#5a6e50]">{problem.body}</p>
                  <span className="mt-5 text-sm font-semibold text-[#3a5c2f] group-hover:underline">
                    Learn more →
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Video + About Section ── */
function AboutSection() {
  return (
    <section className="content-auto bg-dark-earth px-6 py-24">
      <div className="mx-auto grid max-w-[1280px] items-center gap-14 lg:grid-cols-2">
        {/* Video embed placeholder / image */}
        <div className="glass-panel surface-sheen relative aspect-video overflow-hidden rounded-3xl bg-[#0d1a09] shadow-2xl">
          <Image
            src="/images/soil-microorganism-microscope.png"
            alt="Soil microorganisms under microscope — the living community in healthy soil"
            fill
            sizes="(min-width: 1024px) 50vw, 100vw"
            className="object-cover opacity-70"
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <a
              href="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
              target="_blank"
              rel="noopener noreferrer"
              className="w-20 h-20 rounded-full bg-white/20 border-2 border-white/60 flex items-center justify-center hover:bg-white/30 transition-colors backdrop-blur-sm"
            >
              <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </a>
          </div>
          <div className="absolute bottom-4 left-4 text-xs text-white/60 font-mono">
            Soil food web under fluorescence microscopy
          </div>
        </div>

        {/* Content */}
        <div className="reveal-rise">
          <p className="editorial-kicker text-[#a8cc8a] mb-4">Our Approach</p>
          <h2 className="font-serif text-[2.5rem] md:text-[3rem] text-white leading-tight tracking-[-0.04em] mb-6">
            The Bio Soil Approach to Soil Regeneration
          </h2>
          <p className="text-[#9ab88a] leading-8 mb-5">
            The complete soil food web can be found in virgin soils around the world. Once disrupted
            by chemical inputs, tillage, and monoculture, it must be deliberately and methodically
            restored.
          </p>
          <p className="text-[#9ab88a] leading-8 mb-8">
            Using BioComplete™ soil amendments aligned with the soil food web science, most soils
            can be regenerated in the first growing season — with measurable, quantifiable results
            tracked through our analysis platform.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link
              href="/science"
              className="button-glow rounded-full bg-[#3a5c2f] px-6 py-3.5 text-sm font-semibold text-white hover:bg-[#4e7a40] transition-colors"
            >
              How It Works
            </Link>
            <Link
              href="/silksoil"
              className="button-glow rounded-full border border-white/20 px-6 py-3.5 text-sm font-semibold text-white hover:bg-white/10 transition-colors"
            >
              Test Your Soil
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ── Photo Feature: Scientist & Farm ── */
function PhotoFeatureSection() {
  return (
    <section className="content-auto bg-[#f5efdf] px-6 py-24">
      <div className="mx-auto grid max-w-[1280px] gap-6 md:grid-cols-2">
        {/* Left: scientist */}
        <div className="relative rounded-3xl overflow-hidden min-h-[440px] group card-hover">
          <Image
            src="/images/soil-scientist-hands.png"
            alt="Scientist holding healthy soil showing living root and fungi networks"
            fill
            sizes="(min-width: 768px) 50vw, 100vw"
            className="object-cover group-hover:scale-105 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[rgba(18,26,12,0.75)] to-transparent" />
          <div className="absolute bottom-0 left-0 p-8">
            <p className="editorial-kicker text-[#a8cc8a] mb-2">In the field</p>
            <h3 className="font-serif text-2xl text-white mb-2">
              Living soil you can see and feel
            </h3>
            <p className="text-[#c0d8a8] text-sm leading-6 max-w-xs">
              Healthy soil teems with organisms visible to the naked eye — earthworms, fungi
              strands, and structured aggregates.
            </p>
          </div>
        </div>

        {/* Right: farm */}
        <div className="relative rounded-3xl overflow-hidden min-h-[440px] group card-hover">
          <Image
            src="/images/healthy-farm-field.png"
            alt="Healthy regenerative farm field at golden hour showing thriving crops"
            fill
            sizes="(min-width: 768px) 50vw, 100vw"
            className="object-cover group-hover:scale-105 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[rgba(18,26,12,0.75)] to-transparent" />
          <div className="absolute bottom-0 left-0 p-8">
            <p className="editorial-kicker text-[#a8cc8a] mb-2">Results on six continents</p>
            <h3 className="font-serif text-2xl text-white mb-2">Measurable yield improvements</h3>
            <p className="text-[#c0d8a8] text-sm leading-6 max-w-xs">
              Farmers report yield increases of up to 150% in the first season after restoring their
              soil food web.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ── SilkSoil CTA Spotlight ── */
function CalculatorSpotlight({ session }: { session: SessionResponse | null }) {
  const ctaHref = session ? "/silksoil" : "/login";
  const ctaLabel = session ? "Open SilkSoil — Member Access" : "Sign In to Access SilkSoil";
  const insightPills = ["Live scoring", "Microbial ratios", "Decision-ready"];

  return (
    <section className="content-auto bg-cream-section px-6 py-24">
      <div className="mx-auto max-w-[1280px]">
        <div className="overflow-hidden rounded-[36px] bg-[#1e3318] shadow-2xl">
          <div className="grid items-stretch lg:grid-cols-[1fr_1fr]">
            {/* Content */}
            <div className="relative flex flex-col justify-center overflow-hidden p-10 md:p-14">
              <div className="absolute inset-0 pointer-events-none">
                <div className="absolute left-[12%] top-[16%] h-40 w-40 rounded-full bg-[rgba(138,210,179,0.08)] blur-3xl" />
                <div className="absolute right-[6%] bottom-[8%] h-56 w-56 rounded-full bg-[rgba(212,147,61,0.1)] blur-3xl" />
              </div>
              <div className="relative z-10">
                <div className="mb-4 flex flex-wrap gap-3">
                  {insightPills.map((pill) => (
                    <span key={pill} className="signal-pill">
                      {pill}
                    </span>
                  ))}
                </div>
                <p className="editorial-kicker mb-4 text-[#a8cc8a]">New Feature</p>
                <h2 className="mb-5 font-serif text-[2.4rem] leading-tight tracking-[-0.04em] text-white md:text-[3rem]">
                  SilkSoil
                </h2>
                <p className="mb-4 leading-8 text-[#9ab88a]">
                  Enter your soil measurements — pH, organic matter, temperature, moisture,
                  microbial indicators — and receive a comprehensive Soil Health Score with
                  actionable recommendations.
                </p>
                <ul className="mb-8 space-y-2 text-sm text-[#8aaa7a]">
                  {[
                    "Fungal-to-Bacterial ratio analysis",
                    "Nutrient availability scoring",
                    "Biological activity index",
                    "Predictive yield improvement estimate",
                    "Personalised restoration roadmap",
                  ].map((f) => (
                    <li key={f} className="flex items-center gap-2.5">
                      <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-[#3a5c2f] text-[10px] font-bold text-white">
                        ✓
                      </span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href={ctaHref}
                  className="button-glow inline-flex self-start rounded-full bg-[#d4933d] px-7 py-4 text-base font-semibold text-white shadow-md transition-colors hover:bg-[#b97849]"
                >
                  {ctaLabel}
                </Link>
              </div>
            </div>

            {/* Decorative image panel */}
            <div className="relative hidden min-h-[400px] lg:block">
              <Image
                src="/images/soil-hero-bg.png"
                alt="Soil texture showing rich biological activity"
                fill
                sizes="(min-width: 1024px) 50vw, 100vw"
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-[#1e3318] via-[rgba(30,51,24,0.72)] to-transparent" />
              <div className="absolute inset-0 flex items-center justify-center p-8">
                <div className="glass-panel surface-sheen w-full max-w-[360px] rounded-[30px] p-7 shadow-xl">
                  <div className="flex items-center justify-between">
                    <p className="panel-label">Your Soil Score</p>
                    <span className="rounded-full border border-[rgba(255,255,255,0.12)] px-3 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-[#dbe9d4]">
                      Preview
                    </span>
                  </div>
                  <p className="mt-4 font-serif text-[4.5rem] font-bold leading-none text-[#d4933d]">
                    84
                  </p>
                  <p className="mt-2 text-sm font-medium text-white">
                    Excellent — Biologically Active
                  </p>
                  <div className="mt-5 h-2 overflow-hidden rounded-full bg-[#2a3a22]">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-[#3a5c2f] via-[#8ad2b3] to-[#d4933d]"
                      style={{ width: "84%" }}
                    />
                  </div>
                  <div className="mt-5 grid grid-cols-2 gap-3">
                    <div className="panel-stat p-4">
                      <p className="panel-label">F:B ratio</p>
                      <p className="mt-2 text-lg font-semibold text-[#dce8d5]">2.4 : 1</p>
                    </div>
                    <div className="panel-stat p-4">
                      <p className="panel-label">Confidence</p>
                      <p className="mt-2 text-lg font-semibold text-[#dce8d5]">High</p>
                    </div>
                  </div>
                  <p className="mt-4 text-xs text-[#6a8a5a]">
                    Signal synthesis combines biology, balance, and habitat readings into one
                    clearer recommendation layer.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ── Stats Strip ── */
function StatsStrip({ stats }: { stats: HomeStat[] }) {
  return (
    <section className="content-auto bg-[#3a5c2f] px-6 py-16">
      <div className="mx-auto max-w-[1280px]">
        <div className="mb-6 flex items-center justify-between gap-4">
          <span className="signal-pill">Proof Layer</span>
          <p className="text-right text-xs uppercase tracking-[0.18em] text-[#b7d0a6]">
            Regeneration metrics observed across field programs
          </p>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {stats.map((stat, index) => (
            <div key={stat.number} className="metric-panel rounded-[26px] p-6 text-center">
              <p className="panel-label text-[#9fbc8a]">Metric 0{index + 1}</p>
              <p className="mt-4 font-serif text-[3.2rem] font-bold leading-none text-[#d4933d]">
                {stat.number}
              </p>
              <p className="mt-3 text-sm font-semibold text-white">{stat.label}</p>
              <p className="mt-1 text-xs text-[#9ab88a]">{stat.sub}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Testimonials ── */
function TestimonialsSection({ testimonials }: { testimonials: Testimonial[] }) {
  return (
    <section className="content-auto bg-[#f5efdf] px-6 py-24">
      <div className="mx-auto max-w-[1280px]">
        <div className="mb-14 grid gap-8 lg:grid-cols-[minmax(0,1.15fr)_minmax(300px,0.85fr)] lg:items-end">
          <div className="section-frame">
            <p className="editorial-kicker mb-3 text-[#3a5c2f]">What our community says</p>
            <h2 className="font-serif text-[2.4rem] tracking-[-0.03em] text-[#1e3318] md:text-[3rem]">
              Proven on Six Continents
            </h2>
          </div>
          <div className="paper-tech-card rounded-[30px] p-6">
            <div className="relative z-10">
              <span className="signal-chip-light">Field voices</span>
              <p className="mt-4 text-sm leading-7 text-[#54644b]">
                The strongest signal is repeatable feedback from growers, consultants, and
                scientists applying the approach in very different climates.
              </p>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((t, index) => (
            <div
              key={t.author}
              className="paper-tech-card card-hover rounded-3xl p-7 flex flex-col"
            >
              <div className="relative z-10 flex h-full flex-col">
                <div className="mb-4 flex items-center justify-between">
                  <svg
                    className="h-8 w-8 shrink-0 text-[#d4933d]"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                  </svg>
                  <span className="signal-chip-light">0{index + 1}</span>
                </div>
                <p className="flex-1 text-sm italic leading-7 text-[#4a5e40]">
                  &ldquo;{t.quote}&rdquo;
                </p>
                <div className="mt-6 border-t border-[rgba(58,92,47,0.1)] pt-5">
                  <p className="text-sm font-semibold text-[#1e3318]">{t.author}</p>
                  <p className="mt-0.5 text-xs text-[#6a8060]">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Blog Preview ── */
type BlogPreviewPost = Partial<BlogPostSummary> & {
  title: string;
  category: string;
  excerpt?: string | null;
  date?: string;
  readTime?: string;
};

function BlogSection({ posts }: { posts: BlogPreviewPost[] }) {
  return (
    <section className="content-auto bg-dark-earth px-6 py-24">
      <div className="mx-auto max-w-[1280px]">
        <div className="mb-12 grid gap-8 lg:grid-cols-[minmax(0,1.2fr)_minmax(300px,0.8fr)] lg:items-end">
          <div className="section-frame">
            <p className="editorial-kicker mb-3 text-[#a8cc8a]">Latest from the field</p>
            <h2 className="font-serif text-[2.4rem] tracking-[-0.03em] text-white">
              News & Updates
            </h2>
          </div>
          <div className="glass-panel rounded-[30px] p-6">
            <div className="flex items-center justify-between gap-4">
              <span className="signal-pill">Research feed</span>
              <Link
                href="/blog"
                className="link-sweep text-sm font-semibold text-[#a8cc8a] transition-colors hover:text-white"
              >
                View all articles →
              </Link>
            </div>
            <p className="mt-4 text-sm leading-7 text-[#a7bf99]">
              A live mix of scientific explainers, field case studies, and product updates for
              growers tracking biological performance over time.
            </p>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {posts.map((post) => (
            <Link
              key={post.title}
              href={post.slug ? `/blog/${post.slug}` : "/blog"}
              className="group"
            >
              <div className="glass-panel dark-card-sheen card-hover h-full rounded-3xl p-7 flex flex-col hover:bg-[rgba(255,255,255,0.07)] transition-colors">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <span className="tag-pill bg-[rgba(168,204,138,0.12)] text-[#a8cc8a] border border-[rgba(168,204,138,0.2)]">
                    {post.category}
                  </span>
                  <span className="text-xs text-[#5a7050]">
                    {post.read_time_minutes ? `${post.read_time_minutes} min read` : post.readTime}
                  </span>
                </div>
                <h3 className="font-serif text-xl text-white leading-snug mb-3 flex-1 group-hover:text-[#c8e0a8] transition-colors relative z-10">
                  {post.title}
                </h3>
                <p className="text-sm text-[#6a8a5a] leading-6 mb-5 relative z-10">
                  {post.excerpt ?? "Read the latest update from the Bio Soil team."}
                </p>
                <div className="relative z-10 flex items-center justify-between text-xs text-[#5a7050]">
                  <span>
                    {post.published_at
                      ? new Date(post.published_at).toLocaleDateString("en-GB", {
                          month: "long",
                          year: "numeric",
                        })
                      : post.date}
                  </span>
                  <span className="group-hover:text-[#a8cc8a] transition-colors">Read more →</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Page (Server Component) ── */
export default async function MarketingHomePage() {
  const [{ pageData, featuredPosts }, session] = await Promise.all([
    getHomeData(),
    getServerSession(),
  ]);
  const page = pageData?.page;
  const sections: HomeSections = (pageData?.sections as HomeSections | undefined) ?? {};

  const problems: HomeProblem[] = sections.problems ?? FALLBACK_PROBLEMS;
  const stats: HomeStat[] = sections.stats ?? FALLBACK_STATS;
  const testimonials: Testimonial[] = sections.testimonials ?? FALLBACK_TESTIMONIALS;
  // Use featured posts from DB, or fall back to static placeholders
  const blogPosts: BlogPreviewPost[] =
    featuredPosts.length > 0
      ? featuredPosts
      : [
          {
            title: "How Mycorrhizal Fungi Networks Drive Nutrient Cycling",
            category: "Science",
            excerpt:
              "Underground fungal highways transport nutrients between plants and microorganisms.",
            published_at: "2026-04-03",
            read_time_minutes: 6,
            slug: "mycorrhizal-fungi-nutrient-cycling",
          },
          {
            title: "Pakistani Farm Soil Restored in One Season",
            category: "Case Studies",
            excerpt: "The soil food web approach transformed degraded farmland in Pakistan.",
            published_at: "2026-03-28",
            read_time_minutes: 8,
            slug: "pakistani-farm-soil-restored",
          },
          {
            title: "SilkSoil: New Microbiome Scoring Module Released",
            category: "Updates",
            excerpt: "Our latest calculator update adds fungal-to-bacterial ratio scoring.",
            published_at: "2026-03-20",
            read_time_minutes: 4,
            slug: "silksoil-microbiome-scoring",
          },
        ];

  return (
    <>
      <Hero page={page} stats={stats} />
      <ProblemsSection problems={problems} />
      <AboutSection />
      <PhotoFeatureSection />
      <CalculatorSpotlight session={session} />
      <StatsStrip stats={stats} />
      <TestimonialsSection testimonials={testimonials} />
      <BlogSection posts={blogPosts} />
    </>
  );
}

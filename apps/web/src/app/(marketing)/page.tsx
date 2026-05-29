import Image from "next/image";
import Link from "next/link";
import { getCmsPage, getFeaturedPosts } from "@/lib/cmsData";
import { getServerSession } from "@/lib/server-session";
import { ProblemArticleSection } from "@/features/home/problem-article-section";
import type { SessionResponse } from "@bio/api-client";
import type {
  BlogPostSummary,
  CmsPage,
  HomeProblem,
  HomeSections,
  HomeStat,
  Testimonial,
} from "@/lib/cmsTypes";

export const revalidate = 60;

async function getHomeData() {
  try {
    const [pageData, featuredPosts] = await Promise.all([getCmsPage("home"), getFeaturedPosts()]);
    return { pageData, featuredPosts: featuredPosts ?? [] };
  } catch {
    return { pageData: null, featuredPosts: [] };
  }
}

const FALLBACK_PROBLEMS: HomeProblem[] = [
  {
    title: "An Agricultural Revolution Is Unfolding in India",
    subtitle: "Case Study",
    body: "How Andhra Pradesh's APCNF program reached 851,000 farming households by working with nature instead of against it.",
    icon: "shield",
    link: "/science/agricultural-revolution-india",
    image: "/images/article-india-farming.png",
  },
  {
    title: "Turning Waste into Life: Household Vermicomposting",
    subtitle: "Practice Guide",
    body: "Every kitchen generates soil gold. Learn how household vermicomposting converts scraps into biologically active compost.",
    icon: "yield",
    link: "/science/household-vermicomposting",
    image: "/images/article-vermicomposting.png",
  },
  {
    title: "From China to Brazil: Two Paths, One Wisdom",
    subtitle: "Comparative Study",
    body: "Chinese soil scientist Guangjiong Hou and Swiss agroforester Ernst Götsch arrived at the same answer: cooperate with nature.",
    icon: "ecosystem",
    link: "/science/china-brazil-two-paths",
    image: "/images/article-china-brazil-agroforestry.png",
  },
  {
    title: "From Kitchen Scraps to Soil Gold",
    subtitle: "Home Practice",
    body: "A seedling growing from dark organic soil tells a story of regeneration. Set up your first worm bin at home.",
    icon: "structure",
    link: "/science/soil-organic-matter-seedling",
    image: "/images/article-seedling-soil.png",
  },
];

const FALLBACK_STATS: HomeStat[] = [
  { number: "150%", label: "Reported yield increase", sub: "In the first growing season" },
  { number: "100%", label: "Reduction in pest damage", sub: "Using natural food web protection" },
  { number: "60%", label: "Cut in fertilizer costs", sub: "After soil biology restored" },
  { number: "6", label: "Continents with proven results", sub: "Farmers transformed worldwide" },
];

const FALLBACK_TESTIMONIALS: Testimonial[] = [
  {
    quote:
      "Our farm was in serious trouble, but after implementing the soil food web approach we increased our yield in a single season.",
    author: "Hassan A.",
    role: "Grain Farmer",
  },
  {
    quote: "Bio Soil explains soil biology in a way our team can finally apply in the field.",
    author: "Meredith L.",
    role: "Horticulturist",
  },
  {
    quote: "The calculator and science resources helped us connect lab results to practical decisions.",
    author: "Sara M.",
    role: "Regenerative Farmer",
  },
];

type BlogPreviewPost = Partial<BlogPostSummary> & {
  title: string;
  category: string;
  excerpt?: string | null;
  date?: string;
  readTime?: string;
  link?: string;
};

const STEP_ITEMS = [
  {
    eyebrow: "Step 01",
    title: "Identify missing biology",
    body: "Use microscopy, field context, and soil measurements to understand which functional groups are weak or absent.",
  },
  {
    eyebrow: "Step 02",
    title: "Boost microbial numbers",
    body: "Support the biology with compost, extracts, food sources, and practices that rebuild the living network.",
  },
  {
    eyebrow: "Step 03",
    title: "Keep the system alive",
    body: "Adopt management that protects oxygen, moisture, aggregates, roots, and the organisms doing the work.",
  },
];

function Hero({ page }: { page: CmsPage | undefined }) {
  return (
    <section className="reference-hero relative min-h-[calc(100svh-92px)] overflow-hidden px-6">
      <Image
        src="/images/soil-hands-bg.jpg"
        alt="Hands working with living soil"
        fill
        priority
        sizes="100vw"
        className="object-cover"
      />
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(14,28,12,0.88),rgba(14,28,12,0.55)_46%,rgba(14,28,12,0.2)),linear-gradient(180deg,rgba(14,28,12,0.1),rgba(14,28,12,0.72))]" />
      <div className="relative mx-auto flex min-h-[calc(100svh-92px)] max-w-[1280px] items-center py-10 md:py-12">
        <div className="max-w-[940px]">
          <p className="editorial-kicker mb-3 text-[#cde7b8]">Our Mission</p>
          <h1 className="max-w-[800px] font-serif text-[2.2rem] leading-tight tracking-[-0.02em] text-white md:text-[3.8rem] lg:text-[4.2rem]">
            Restoring the web of life beneath your soil.
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-6 text-[#d1dfc5] md:text-base">
            Discover how biology replaces chemicals to boost yields, suppress pests, and sequester carbon. Build living soil from the ground up.
          </p>
          <div className="mt-6 flex flex-wrap gap-4">
            <Link
              href="/silksoil"
              className="button-glow rounded-full bg-[#d4933d] px-6 py-3 text-xs font-bold uppercase tracking-[0.08em] text-white shadow-xl"
            >
              Test Your Soil
            </Link>
            <Link
              href="/science"
              className="button-glow rounded-full border border-[rgba(168,204,138,0.32)] bg-[rgba(168,204,138,0.08)] px-6 py-3 text-xs font-bold uppercase tracking-[0.08em] text-[#edf5e8] backdrop-blur-md"
            >
              Learn the Method
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

function UpdatesSection({ posts }: { posts: BlogPreviewPost[] }) {
  const featured = posts.slice(0, 4);

  return (
    <section className="reference-updates px-6 py-20">
      <div className="mx-auto max-w-[1280px]">
        <div className="mb-10 flex flex-wrap items-end justify-between gap-6">
          <div>
            <p className="editorial-kicker mb-3 text-[#a8cc8a]">Important Updates</p>
            <h2 className="font-serif text-[2.6rem] leading-tight tracking-[-0.03em] text-[#edf5e8] md:text-[4rem]">
              Latest field notes and science updates.
            </h2>
          </div>
          <Link href="/blog" className="link-sweep font-semibold text-[#d4933d]">
            View all articles
          </Link>
        </div>
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {featured.map((post, index) => (
            <Link
              key={post.slug ?? post.title}
              href={post.link ?? (post.slug ? `/blog/${post.slug}` : "/blog")}
              className="update-tile group min-h-[290px] rounded-[28px] p-6"
            >
              <p className="editorial-kicker text-[#a8cc8a]">{post.category}</p>
              <h3 className="mt-5 font-serif text-[1.45rem] leading-tight text-[#edf5e8] transition-colors group-hover:text-[#d4933d]">
                {post.title}
              </h3>
              <p className="mt-4 text-sm leading-7 text-[#a9c09d]">
                {post.excerpt ?? "Read the latest update from the Bio Soil team."}
              </p>
              <div className="mt-6 flex items-center justify-between text-xs font-semibold uppercase tracking-[0.12em] text-[#7fa177]">
                <span>0{index + 1}</span>
                <span>{post.read_time_minutes ? `${post.read_time_minutes} min` : post.readTime}</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

function ApproachSection() {
  return (
    <section className="reference-approach bg-[#173011] px-6 py-24 text-white">
      <div className="mx-auto grid max-w-[1280px] items-center gap-14 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="relative min-h-[420px] overflow-hidden rounded-[34px]">
          <Image
            src="/images/soil-microorganism-microscope.png"
            alt="Soil food web under microscope"
            fill
            sizes="(min-width: 1024px) 45vw, 100vw"
            className="object-cover"
          />
          <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(15,30,12,0.04),rgba(15,30,12,0.54))]" />
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="flex h-24 w-24 items-center justify-center rounded-full border border-[rgba(168,204,138,0.38)] bg-[rgba(168,204,138,0.14)] text-3xl text-[#edf5e8] backdrop-blur-md transition-transform hover:scale-105">
              ▶
            </span>
          </div>
          <p className="absolute bottom-5 left-6 font-mono text-xs text-white/65">
            Soil food web under fluorescence microscopy
          </p>
        </div>
        <div>
          <p className="editorial-kicker mb-4 text-[#a8cc8a]">The Bio Soil Approach</p>
          <h2 className="font-serif text-[2.7rem] leading-tight tracking-[-0.04em] md:text-[4.5rem]">
            Soil regeneration starts with restoring the living network.
          </h2>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-[#b8d0aa]">
            The approach is simple to understand and rigorous to apply: diagnose the biology, rebuild
            the missing groups, then protect the conditions that let them survive.
          </p>
          <div className="mt-10 space-y-4">
            {STEP_ITEMS.map((step) => (
              <div key={step.title} className="approach-row grid gap-4 border-t border-white/12 py-5 md:grid-cols-[120px_1fr]">
                <p className="editorial-kicker text-[#d4933d]">{step.eyebrow}</p>
                <div>
                  <h3 className="font-serif text-2xl text-white">{step.title}</h3>
                  <p className="mt-2 max-w-2xl text-sm leading-7 text-[#a9c09d]">{step.body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function ProofSection({ stats, testimonials }: { stats: HomeStat[]; testimonials: Testimonial[] }) {
  return (
    <section className="proof-section px-6 py-24">
      <div className="mx-auto max-w-[1280px]">
        <div className="grid gap-10 lg:grid-cols-[0.92fr_1.08fr] lg:items-end">
          <div>
            <p className="editorial-kicker mb-3 text-[#a8cc8a]">Measurable Impact</p>
            <h2 className="max-w-3xl font-serif text-[2.2rem] leading-tight tracking-[-0.02em] text-[#edf5e8] md:text-[3.8rem]">
              Biology does the heavy lifting.
            </h2>
          </div>
          <p className="max-w-xl text-sm leading-6 text-[#adc6a0]">
            Regenerating the soil food web restores natural balances, radically cutting input costs and restoring true fertility to the land.
          </p>
        </div>
        <div className="mt-14 grid gap-6 md:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="proof-stat">
              <p className="font-serif text-[4rem] leading-none text-[#d4933d]">{stat.number}</p>
              <p className="mt-4 font-semibold text-[#edf5e8]">{stat.label}</p>
              <p className="mt-2 text-sm leading-6 text-[#98b58d]">{stat.sub}</p>
            </div>
          ))}
        </div>
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {testimonials.slice(0, 3).map((testimonial) => (
            <figure key={testimonial.author} className="testimonial-panel">
              <blockquote className="text-lg leading-8 text-[#d6e5cf]">
                &ldquo;{testimonial.quote}&rdquo;
              </blockquote>
              <figcaption className="mt-6 text-sm font-semibold text-[#d4933d]">
                {testimonial.author}
                <span className="block pt-1 font-normal text-[#8eaa82]">{testimonial.role}</span>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}

function EcosystemSection() {
  return (
    <section className="ecosystem-section relative overflow-hidden px-6 py-24 text-white">
      <Image
        src="/images/healthy-farm-field.png"
        alt="Regenerative farm landscape"
        fill
        sizes="100vw"
        className="object-cover"
      />
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(12,26,10,0.9),rgba(12,26,10,0.58)_52%,rgba(12,26,10,0.24)),linear-gradient(180deg,rgba(12,26,10,0.16),rgba(12,26,10,0.78))]" />
      <div className="relative mx-auto max-w-[1280px]">
        <p className="editorial-kicker mb-3 text-[#cde7b8]">Healthy Ecosystem</p>
        <h2 className="max-w-3xl font-serif text-[2.2rem] leading-tight tracking-[-0.02em] md:text-[3.8rem]">
          Biology connects fertility, water, and carbon.
        </h2>
        <div className="mt-12 grid gap-4 md:grid-cols-3">
          {["Nutrient cycling", "Disease suppression", "Soil structure"].map((item) => (
            <div key={item} className="ecosystem-chip">
              {item}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function MovementSection({ session }: { session: SessionResponse | null }) {
  return (
    <section className="bg-[#173011] px-6 py-24 text-white">
      <div className="mx-auto grid max-w-[1280px] gap-10 lg:grid-cols-[1fr_0.8fr] lg:items-center">
        <div>
          <p className="editorial-kicker mb-3 text-[#a8cc8a]">Join the Movement</p>
          <h2 className="max-w-2xl font-serif text-[2.2rem] leading-tight tracking-[-0.02em] md:text-[3.8rem]">
            Start with the science.
          </h2>
        </div>
        <div className="movement-panel">
          <p className="text-sm leading-7 text-[#c2d7b7]">
            Use SilkSoil to organize soil measurements, understand biological constraints, and turn
            article content into a practical learning path.
          </p>
          <Link
            href={session ? "/silksoil" : "/login"}
            className="mt-8 inline-flex rounded-full bg-[#d4933d] px-7 py-4 text-sm font-bold uppercase tracking-[0.08em] text-white"
          >
            {session ? "Open SilkSoil" : "Sign In to Start"}
          </Link>
        </div>
      </div>
    </section>
  );
}

export default async function MarketingHomePage() {
  const [{ pageData, featuredPosts }, session] = await Promise.all([
    getHomeData(),
    getServerSession(),
  ]);
  const page = pageData?.page;
  const sections: HomeSections = (pageData?.sections as HomeSections | undefined) ?? {};

  const problems = FALLBACK_PROBLEMS;
  const stats = sections.stats ?? FALLBACK_STATS;
  const testimonials = sections.testimonials ?? FALLBACK_TESTIMONIALS;
  const blogPosts: BlogPreviewPost[] =
    featuredPosts.length > 0
      ? featuredPosts
      : [
          {
            title: "An Agricultural Revolution Is Unfolding in India",
            category: "Case Study",
            excerpt: "How Andhra Pradesh's APCNF program reached 851,000 farming households by working with nature instead of against it.",
            published_at: "2025-08-21",
            read_time_minutes: 8,
            slug: "agricultural-revolution-india",
            link: "/science/agricultural-revolution-india",
          },
          {
            title: "Turning Waste into Life: Household Vermicomposting",
            category: "Practice Guide",
            excerpt: "Every kitchen generates soil gold. Learn how household vermicomposting converts scraps into biologically active compost.",
            published_at: "2025-10-25",
            read_time_minutes: 7,
            slug: "household-vermicomposting",
            link: "/science/household-vermicomposting",
          },
          {
            title: "From China to Brazil: Two Paths, One Wisdom",
            category: "Comparative Study",
            excerpt: "Chinese soil scientist Guangjiong Hou and Swiss agroforester Ernst Götsch arrived at the same answer: cooperate with nature.",
            published_at: "2025-08-29",
            read_time_minutes: 10,
            slug: "china-brazil-two-paths",
            link: "/science/china-brazil-two-paths",
          },
          {
            title: "From Kitchen Scraps to Soil Gold",
            category: "Home Practice",
            excerpt: "A seedling growing from dark organic soil tells a story of regeneration. Set up your first worm bin at home.",
            published_at: "2025-10-25",
            read_time_minutes: 6,
            slug: "soil-organic-matter-seedling",
            link: "/science/soil-organic-matter-seedling",
          },
        ];

  return (
    <>
      <Hero page={page} />
      <ProblemArticleSection problems={problems} />
      <EcosystemSection />
      <ProofSection stats={stats} testimonials={testimonials} />
      <MovementSection session={session} />
    </>
  );
}

import Link from "next/link";
import Image from "next/image";
import { getCmsPage } from "@/lib/cmsData";
import type { CmsPage, ScienceSections } from "@/lib/cmsTypes";

export const revalidate = 60;

const ARTICLES = [
  {
    slug: "agricultural-revolution-india",
    title: "An Agricultural Revolution Is Unfolding in India",
    category: "Case Study",
    date: "August 21, 2025",
    readTime: "8 min read",
    excerpt:
      "How Andhra Pradesh's APCNF program reached 851,000 farming households by working with nature instead of against it — with 27% higher net profits and healthier soil.",
    image: "/images/article-india-farming.webp",
    imageAlt: "Indian farmer tending crops in lush terraced rice fields",
  },
  {
    slug: "household-vermicomposting",
    title: "Turning Waste into Life: The Microscopic Miracle of Household Vermicomposting",
    category: "Practice Guide",
    date: "October 25, 2025",
    readTime: "7 min read",
    excerpt:
      "Every kitchen generates soil gold. With earthworms and organic matter, household vermicomposting converts scraps into biologically active compost richer than anything you can buy.",
    image: "/images/article-vermicomposting.webp",
    imageAlt: "Wooden compost bin with red earthworms on rich dark soil and vegetable scraps",
  },
  {
    slug: "china-brazil-two-paths",
    title: "From China to Brazil: Two Paths, One Wisdom",
    category: "Comparative Study",
    date: "August 29, 2025",
    readTime: "10 min read",
    excerpt:
      "Chinese soil scientist Guangjiong Hou and Swiss agroforester Ernst Götsch worked on opposite sides of the globe but arrived at the same answer: cooperate with nature.",
    image: "/images/article-china-brazil-agroforestry.webp",
    imageAlt: "Aerial view of rice paddies beside tropical forest illustrating syntropic contrast",
  },
  {
    slug: "soil-organic-matter-seedling",
    title: "From Kitchen Scraps to Soil Gold: Starting Your Home Compost",
    category: "Home Practice",
    date: "October 25, 2025",
    readTime: "6 min read",
    excerpt:
      "A seedling growing from dark organic soil tells a story of regeneration. Learn the step-by-step process of setting up your first worm bin and building living soil at home.",
    image: "/images/article-seedling-soil.webp",
    imageAlt: "Young green seedling growing in rich organic soil in a terracotta pot",
  },
];


export default async function SciencePage() {
  let page: CmsPage | null = null;
  let sections: ScienceSections = {};
  try {
    const data = await getCmsPage("science");
    page = data?.page ?? null;
    sections = (data?.sections as ScienceSections | undefined) ?? {};
  } catch {
    /* fallback */
  }



  const heroKicker = page?.hero_kicker ?? "Peer-reviewed science, practical results";
  const heroHeading = page?.hero_heading ?? "How the Soil Food Web Works";
  const heroSub =
    page?.hero_subheading ??
    "Understanding the science behind the soil food web is the foundation of everything we do.";

  return (
    <div className="min-h-screen bg-[#f5efdf]">
      {/* Hero */}
      <section className="content-auto bg-dark-earth px-6 py-20 text-center">
        <div className="mx-auto max-w-[800px]">
          <p className="editorial-kicker text-[#a8cc8a] mb-4">{heroKicker}</p>
          <h1 className="font-serif text-[3rem] md:text-[4.5rem] text-white leading-tight tracking-[-0.04em] mb-5">
            {heroHeading}
          </h1>
          <p className="text-[#9ab88a] text-lg leading-8">{heroSub}</p>
        </div>
      </section>


      {/* Featured Articles */}
      <section className="content-auto bg-[#f5efdf] px-6 py-20">
        <div className="mx-auto max-w-[1100px]">
          <div className="text-center mb-14">
            <p className="editorial-kicker text-[#3a5c2f] mb-3">From the field</p>
            <h2 className="font-serif text-[2.4rem] text-[#1e3318] tracking-[-0.03em]">
              Featured Research Articles
            </h2>
            <p className="mt-4 text-[#4a5e40] max-w-[560px] mx-auto leading-7">
              Real-world case studies and practice guides from the Soil Vitality Research Lab and partner agroecology programs.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {ARTICLES.map((article) => (
              <Link
                key={article.slug}
                href={`/science/${article.slug}`}
                prefetch={true}
                className="group block"
              >
                <div className="h-full rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white overflow-hidden card-hover">
                  <div className="relative h-56 overflow-hidden">
                    <Image
                      src={article.image}
                      alt={article.imageAlt}
                      fill
                      sizes="(min-width: 768px) 50vw, 100vw"
                      className="object-cover group-hover:scale-105 transition-transform duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[rgba(18,26,12,0.55)] to-transparent" />
                    <span className="absolute top-4 left-4 rounded-full bg-[rgba(168,204,138,0.18)] border border-[rgba(168,204,138,0.3)] px-3 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-[#a8cc8a]">
                      {article.category}
                    </span>
                  </div>
                  <div className="p-7">
                    <div className="flex items-center gap-3 text-xs text-[#7a9a6a] mb-3">
                      <span>{article.date}</span>
                      <span>·</span>
                      <span>{article.readTime}</span>
                    </div>
                    <h3 className="font-serif text-[1.35rem] text-[#1e3318] leading-snug mb-3 group-hover:text-[#3a5c2f] transition-colors">
                      {article.title}
                    </h3>
                    <p className="text-sm text-[#4a5e40] leading-6 mb-4">
                      {article.excerpt}
                    </p>
                    <span className="text-sm font-semibold text-[#3a5c2f] group-hover:text-[#1e3318] transition-colors">
                      Read article →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

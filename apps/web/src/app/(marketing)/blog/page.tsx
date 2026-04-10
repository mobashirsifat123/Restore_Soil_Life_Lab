import Link from "next/link";

import { getPublishedPosts } from "@/lib/cmsData";
import {
  FALLBACK_MARKETING_POSTS,
  dateLabel,
  normalizeBlogSummary,
  type MarketingBlogPost,
} from "@/lib/marketing-blog";

export const revalidate = 60;

type BlogPageProps = {
  searchParams?: Promise<{
    category?: string | string[];
  }>;
};

function normalizeCategory(value: string | string[] | undefined): string {
  const raw = Array.isArray(value) ? value[0] : value;
  if (!raw) {
    return "All";
  }
  return raw.trim();
}

export default async function BlogPage({ searchParams }: BlogPageProps) {
  const resolvedSearchParams = await searchParams;
  let posts: MarketingBlogPost[] = FALLBACK_MARKETING_POSTS;
  try {
    const published = await getPublishedPosts();
    if (published?.length) {
      posts = published.map(normalizeBlogSummary);
    }
  } catch {
    posts = FALLBACK_MARKETING_POSTS;
  }

  const categories = ["All", ...Array.from(new Set(posts.map((post) => post.category)))];
  const requestedCategory = normalizeCategory(resolvedSearchParams?.category);
  const activeCategory = categories.includes(requestedCategory) ? requestedCategory : "All";
  const filtered =
    activeCategory === "All" ? posts : posts.filter((post) => post.category === activeCategory);

  return (
    <div className="min-h-screen bg-[#f5efdf]">
      <section className="bg-dark-earth content-auto px-6 py-20">
        <div className="mx-auto max-w-[800px] text-center">
          <p className="editorial-kicker mb-4 text-[#a8cc8a]">From the field</p>
          <h1 className="font-serif mb-5 text-[3rem] leading-tight tracking-[-0.04em] text-white md:text-[4rem]">
            News, Science & Stories
          </h1>
          <p className="text-lg leading-8 text-[#9ab88a]">
            Insights from our soil scientists, case studies from the field, and updates from the Bio
            Soil community around the world.
          </p>
        </div>
      </section>

      <section className="content-auto border-b border-[rgba(58,92,47,0.1)] bg-[#f0e9d4] px-6 py-10">
        <div className="mx-auto flex max-w-[1100px] flex-wrap gap-2">
          {categories.map((category) => (
            <Link
              key={category}
              href={category === "All" ? "/blog" : `/blog?category=${encodeURIComponent(category)}`}
              className={`rounded-full px-5 py-2.5 text-sm font-semibold transition-all duration-150 ${
                activeCategory === category
                  ? "bg-[#3a5c2f] text-white shadow-sm"
                  : "border border-[rgba(58,92,47,0.15)] bg-white text-[#4a5e40] hover:border-[#3a5c2f] hover:bg-[#edf7e8]"
              }`}
            >
              {category}
            </Link>
          ))}
        </div>
      </section>

      <section className="content-auto px-6 py-16">
        <div className="mx-auto max-w-[1100px]">
          {filtered.length === 0 ? (
            <p className="py-16 text-center text-[#6a8060]">No posts found in this category.</p>
          ) : (
            <div className="stagger grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filtered.map((post) => (
                <Link key={post.slug} href={`/blog/${post.slug}`} className="group">
                  <div className="card-hover flex h-full flex-col rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-7">
                    <div className="mb-4 flex items-center gap-3">
                      <span className="tag-pill">{post.category}</span>
                      <span className="text-xs text-[#9ab888]">
                        {post.readTimeMinutes} min read
                      </span>
                    </div>
                    <h2 className="font-serif mb-3 flex-1 text-[1.25rem] leading-snug text-[#1e3318] transition-colors group-hover:text-[#3a5c2f]">
                      {post.title}
                    </h2>
                    <p className="mb-5 line-clamp-3 text-sm leading-7 text-[#5a6e50]">
                      {post.excerpt}
                    </p>
                    <div className="mt-auto flex items-center justify-between border-t border-[rgba(58,92,47,0.1)] pt-4 text-xs text-[#8aaa7a]">
                      <span>
                        {post.author} · {dateLabel(post.date)}
                      </span>
                      <span className="font-semibold text-[#3a5c2f] group-hover:underline">
                        Read →
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="content-auto bg-[#1e3318] px-6 py-20">
        <div className="mx-auto max-w-[600px] text-center">
          <p className="editorial-kicker mb-3 text-[#a8cc8a]">Stay informed</p>
          <h2 className="font-serif mb-4 text-[2rem] tracking-[-0.03em] text-white">
            Get Soil Science Insights Delivered Monthly
          </h2>
          <p className="mb-8 leading-7 text-[#9ab88a]">
            Join farmers, consultants, and scientists receiving Bio Soil updates.
          </p>
          <div className="mx-auto flex max-w-md gap-3">
            <input
              type="email"
              placeholder="your@email.com"
              aria-label="Email address"
              className="flex-1 rounded-full border border-white/20 bg-white/10 px-5 py-3.5 text-sm text-white placeholder:text-[#6a8a5a] focus:outline-none focus:ring-2 focus:ring-[#a8cc8a]/30"
            />
            <button className="button-glow shrink-0 rounded-full bg-[#d4933d] px-6 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-[#b97849]">
              Subscribe
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

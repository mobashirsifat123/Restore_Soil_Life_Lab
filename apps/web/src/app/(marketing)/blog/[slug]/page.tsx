import Link from "next/link";
import { notFound } from "next/navigation";

import { getBlogPost } from "@/lib/cmsData";
import {
  FALLBACK_MARKETING_POSTS,
  dateLabel,
  normalizeBlogDetail,
  type MarketingBlogPost,
} from "@/lib/marketing-blog";

export const revalidate = 60;

type BlogPostPageProps = {
  params: Promise<{ slug: string }>;
};

function parseMarkdownToBlocks(markdown: string): string[] {
  return markdown
    .split(/\n{2,}/)
    .map((block) => block.trim())
    .filter(Boolean);
}

function headingLevel(block: string): "h2" | "h3" | null {
  if (block.startsWith("## ")) {
    return "h3";
  }
  if (block.startsWith("# ")) {
    return "h2";
  }
  return null;
}

function textFromHeading(block: string): string {
  return block.replace(/^#{1,2}\s+/, "").trim();
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const { slug } = await params;
  let post: MarketingBlogPost | null = null;

  try {
    const fromCms = await getBlogPost(slug);
    if (fromCms) {
      post = normalizeBlogDetail(fromCms);
    }
  } catch {
    post = null;
  }

  if (!post) {
    post = FALLBACK_MARKETING_POSTS.find((candidate) => candidate.slug === slug) ?? null;
  }

  if (!post) {
    notFound();
  }

  const bodyBlocks = parseMarkdownToBlocks(
    post.bodyMarkdown || `${post.excerpt}\n\nMore insights coming soon.`,
  );

  return (
    <div className="min-h-screen bg-[#f5efdf]">
      <section className="bg-dark-earth px-6 py-20">
        <div className="mx-auto max-w-[900px]">
          <Link
            href="/blog"
            className="link-sweep text-sm font-semibold uppercase tracking-[0.14em] text-[#a8cc8a]"
          >
            Back to blog
          </Link>
          <p className="editorial-kicker mt-8 text-[#a8cc8a]">{post.category}</p>
          <h1 className="font-serif mt-4 text-[2.5rem] leading-tight tracking-[-0.04em] text-white md:text-[4rem]">
            {post.title}
          </h1>
          <p className="mt-6 max-w-[720px] text-lg leading-8 text-[#b8d1a8]">{post.excerpt}</p>
          <p className="mt-6 text-sm text-[#9ab88a]">
            {post.author} · {dateLabel(post.date)} · {post.readTimeMinutes} min read
          </p>
        </div>
      </section>

      <section className="content-auto px-6 py-16">
        <article className="mx-auto max-w-[800px] rounded-[30px] border border-[rgba(58,92,47,0.12)] bg-white px-7 py-10 shadow-sm md:px-10">
          {bodyBlocks.map((block, index) => {
            const level = headingLevel(block);
            if (level === "h2") {
              return (
                <h2
                  key={`block-${index}`}
                  className="font-serif mb-4 mt-9 text-[1.9rem] leading-tight tracking-[-0.02em] text-[#1e3318] first:mt-0"
                >
                  {textFromHeading(block)}
                </h2>
              );
            }
            if (level === "h3") {
              return (
                <h3
                  key={`block-${index}`}
                  className="font-serif mb-3 mt-8 text-[1.5rem] leading-tight tracking-[-0.02em] text-[#243a1d]"
                >
                  {textFromHeading(block)}
                </h3>
              );
            }
            return (
              <p key={`block-${index}`} className="mb-6 text-[1.02rem] leading-8 text-[#4e6246]">
                {block}
              </p>
            );
          })}
        </article>
      </section>
    </div>
  );
}

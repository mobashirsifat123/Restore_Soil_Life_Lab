import Image from "next/image";
import Link from "next/link";

type ScienceArticleReaderProps = {
  title: string;
  kicker: string;
  excerpt: string;
  pageImageBase: string;
  pageCount: number;
  readTime: string;
  published: string;
};

export function ScienceArticleReader({
  title,
  kicker,
  excerpt,
  pageImageBase,
  pageCount,
  readTime,
  published,
}: ScienceArticleReaderProps) {
  const pages = Array.from({ length: pageCount }, (_, index) => `${pageImageBase}/page-${index + 1}.png`);

  return (
    <main className="science-article-reader min-h-[calc(100svh-92px)] px-6 py-10 md:py-14">
      <div className="mx-auto max-w-[1280px]">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <Link
            href="/"
            className="link-sweep text-xs font-bold uppercase tracking-[0.16em] text-[#a8cc8a]"
          >
            Back to home
          </Link>
        </div>

        <section className="mb-8 grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-end">
          <div>
            <p className="editorial-kicker mb-3 text-[#a8cc8a]">{kicker}</p>
            <h1 className="font-serif text-[2.4rem] leading-tight tracking-[-0.04em] text-white md:text-[4rem]">
              {title}
            </h1>
          </div>
          <div>
            <p className="max-w-2xl text-base leading-8 text-[#b8d1a8]">{excerpt}</p>
            <p className="mt-5 text-xs font-semibold uppercase tracking-[0.14em] text-[#7fa177]">
              {published} / {readTime}
            </p>
          </div>
        </section>

        <article className="science-rendered-article" aria-label={title}>
          {pages.map((page, index) => (
            <Image
              key={page}
              src={page}
              alt={`${title} page ${index + 1}`}
              width={1241}
              height={1754}
              priority={index === 0}
              loading={index === 0 ? "eager" : "lazy"}
              unoptimized
              className="science-rendered-page"
            />
          ))}
        </article>
      </div>
    </main>
  );
}

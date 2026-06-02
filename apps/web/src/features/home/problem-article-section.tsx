"use client";

import Image from "next/image";
import Link from "next/link";
import type { MouseEvent } from "react";
import type { HomeProblem } from "@/lib/cmsTypes";

const ARTICLE_IMAGES = [
  "/images/soil-scientist-hands.png",
  "/images/soil-microorganism-microscope.png",
  "/images/healthy-farm-field.png",
  "/images/soil-hands-bg.jpg",
  "/images/soil-hero-bg.png",
  "/images/soil-scientist-hands.png",
];

function handleTileMove(event: MouseEvent<HTMLAnchorElement>) {
  const tile = event.currentTarget;
  const rect = tile.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  const tiltX = ((y / rect.height - 0.5) * -8).toFixed(2);
  const tiltY = ((x / rect.width - 0.5) * 8).toFixed(2);

  tile.style.setProperty("--cursor-x", `${x}px`);
  tile.style.setProperty("--cursor-y", `${y}px`);
  tile.style.setProperty("--tilt-x", `${tiltX}deg`);
  tile.style.setProperty("--tilt-y", `${tiltY}deg`);
}

function handleTileLeave(event: MouseEvent<HTMLAnchorElement>) {
  const tile = event.currentTarget;
  tile.style.setProperty("--tilt-x", "0deg");
  tile.style.setProperty("--tilt-y", "0deg");
}

export function ProblemArticleSection({ problems }: { problems: HomeProblem[] }) {
  const [featured, ...supporting] = problems;

  return (
    <section className="content-auto problem-article-section px-6 py-24">
      <div className="mx-auto max-w-[1280px]">
        <div className="mb-10">
          <p className="editorial-kicker mb-3 text-[#a8cc8a]">Featured Research</p>
          <h2 className="font-serif text-[2.6rem] leading-tight tracking-[-0.03em] text-white md:text-[3.6rem]">
            Read Our Latest Articles
          </h2>
        </div>

        {featured ? (
          <Link
            href={featured.link}
            prefetch={true}
            className="article-spotlight group mb-8 block"
            onMouseMove={handleTileMove}
            onMouseLeave={handleTileLeave}
          >
            <div className="article-spotlight-inner">
              <div className="relative min-h-[360px] overflow-hidden rounded-[34px] md:min-h-[520px]">
                <Image
                  src={featured.image ?? ARTICLE_IMAGES[0]}
                  alt={featured.title}
                  fill
                  priority
                  sizes="(min-width: 1024px) 58vw, 100vw"
                  className="article-image object-cover"
                />
                <div className="article-gradient" />
                <div className="article-cursor-glow" />
                <div className="absolute inset-x-0 bottom-0 z-10 p-7 md:p-10">
                  <p className="editorial-kicker mb-3 text-[#cde7b8]">{featured.subtitle}</p>
                  <h3 className="max-w-3xl font-serif text-[2.2rem] leading-tight tracking-[-0.03em] text-white md:text-[3.4rem]">
                    {featured.title}
                  </h3>
                  <p className="mt-4 max-w-2xl text-base leading-8 text-[#d8e6cf]">
                    {featured.body}
                  </p>
                  <span className="mt-7 inline-flex rounded-full bg-[#d4933d] px-5 py-3 text-sm font-semibold text-[#13220e] transition-transform group-hover:translate-x-1">
                    Read article
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ) : null}

        <div className="grid gap-7 md:grid-cols-2">
          {supporting.map((problem, index) => (
            <Link
              key={problem.title}
              href={problem.link}
              prefetch={true}
              className={`article-tile group block ${
                supporting.length % 2 === 1 && index === supporting.length - 1
                  ? "md:col-span-2"
                  : ""
              }`}
              onMouseMove={handleTileMove}
              onMouseLeave={handleTileLeave}
            >
              <div className="article-tile-inner">
                <Image
                  src={problem.image ?? (ARTICLE_IMAGES[index + 1] ?? ARTICLE_IMAGES[0])}
                  alt={problem.title}
                  fill
                  sizes="(min-width: 768px) 50vw, 100vw"
                  className="article-image object-cover"
                />
                <div className="article-gradient" />
                <div className="article-cursor-glow" />
                <div className="article-number">0{index + 2}</div>
                <div className="absolute inset-x-0 bottom-0 z-10 p-7">
                  <p className="editorial-kicker mb-2 text-[#cde7b8]">{problem.subtitle}</p>
                  <h3 className="max-w-xl font-serif text-[1.85rem] leading-tight tracking-[-0.02em] text-white">
                    {problem.title}
                  </h3>
                  <p className="mt-3 max-w-md text-sm leading-7 text-[#d2e1c8]">{problem.body}</p>
                  <span className="mt-5 inline-flex text-sm font-semibold text-white transition-transform group-hover:translate-x-1">
                    Read more →
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

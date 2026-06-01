/* eslint-disable @next/next/no-img-element */

import Link from "next/link";

import { getCmsPage } from "@/lib/cmsData";
import type { AboutFounder, AboutSections } from "@/lib/cmsTypes";

export const revalidate = 60;

const FALLBACK_FOUNDER: AboutFounder = {
  eyebrow: "Academic Advisor",
  label: "Associate Professor, Sichuan University",
  name: "Professor Lu Hongyan (卢红雁)",
  image_url: "/images/soil-scientist-hands.png",
  image_alt: "Living soil held in both hands",
  paragraph_one:
    "Professor Lu Hongyan brings Sichuan University's environmental education, circular economy research, and Sino-German sustainability collaboration into the Bio Soil learning platform.",
  paragraph_two:
    "Her work focuses on material flow management, organic waste recycling, and practical pathways for turning environmental knowledge into public education.",
  paragraph_three:
    "She helped build Sichuan University's undergraduate environmental education framework, including its first Environment and Sustainable Development general curriculum.",
  question_heading: "Have a question about our work?",
  question_cta_label: "Connect With Us",
  question_cta_link: "/contact",
};

const PROFILE_HIGHLIGHTS = [
  "Associate Professor, Sichuan University",
  "Ph.D., Saarland University, Germany",
  "Research in material flow management and organic waste recycling",
];

export default async function AboutPage() {
  let sections: AboutSections = {};

  try {
    const data = await getCmsPage("about");
    sections = (data?.sections as AboutSections | undefined) ?? {};
  } catch {
    /* fallback */
  }

  const founder = {
    ...FALLBACK_FOUNDER,
    image_url:
      sections.founder?.image_url?.trim() ||
      sections.intro?.image_url?.trim() ||
      FALLBACK_FOUNDER.image_url,
    image_alt:
      sections.founder?.image_alt?.trim() ||
      FALLBACK_FOUNDER.image_alt,
  };
  const heroKicker = "About";
  const heroHeading = "Soil restoration starts with environmental education.";
  const heroSubheading =
    "Bio Soil translates soil vitality, circular economy, and organic waste recycling research into clear learning tools for regenerative practice.";

  const founderHeading = founder.name?.trim() || FALLBACK_FOUNDER.name || "";
  const founderEyebrow = founder.eyebrow?.trim() || FALLBACK_FOUNDER.eyebrow || "";
  const founderLabel = founder.label?.trim() || "";
  const founderImageUrl = founder.image_url?.trim() || FALLBACK_FOUNDER.image_url || "";
  const founderImageAlt = founder.image_alt?.trim() || FALLBACK_FOUNDER.image_alt || "";
  const founderParagraphs = [
    founder.paragraph_one?.trim(),
    founder.paragraph_two?.trim(),
    founder.paragraph_three?.trim(),
  ].filter(Boolean) as string[];

  return (
    <div className="min-h-screen bg-[#091207] text-[#d7e7ce]">
      <section className="content-auto relative overflow-hidden px-6 py-16 md:py-20">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute left-1/2 top-0 h-[360px] w-[360px] -translate-x-1/2 rounded-full bg-[rgba(138,210,179,0.12)] blur-3xl" />
          <div className="absolute bottom-[-120px] left-[-60px] h-[320px] w-[320px] rounded-full bg-[rgba(212,147,61,0.12)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-[1080px]">
          <p className="editorial-kicker text-[#a8cc8a]">
            {heroKicker}
          </p>
          <h1 className="mt-5 max-w-[780px] font-serif text-[2rem] leading-[1.1] tracking-[-0.03em] text-white md:text-[2.65rem]">
            {heroHeading}
          </h1>
          <p className="mt-6 max-w-[760px] text-base leading-8 text-[#b8d1a8]">
            {heroSubheading}
          </p>
        </div>
      </section>

      <section className="content-auto px-6 pb-20 md:pb-24">
        <div className="mx-auto grid max-w-[1180px] gap-10 lg:grid-cols-[minmax(0,360px)_minmax(0,1fr)] lg:items-start">
          <div className="relative">
            <div className="absolute inset-6 rounded-[28px] bg-[rgba(212,147,61,0.14)] blur-2xl" />
            <div className="relative overflow-hidden rounded-[28px] border border-[rgba(168,204,138,0.14)] bg-[rgba(220,235,211,0.06)] p-3 shadow-[0_28px_80px_rgba(2,6,3,0.45)]">
              <div className="overflow-hidden rounded-[22px] bg-[#152811]">
                {/* CMS/media URLs can be local or remote, so a plain img keeps this block flexible. */}
                <img
                  src={founderImageUrl}
                  alt={founderImageAlt}
                  loading="lazy"
                  decoding="async"
                  className="aspect-[4/5] h-full w-full object-cover"
                />
              </div>
            </div>
            <div className="mt-5 rounded-[22px] border border-[rgba(168,204,138,0.14)] bg-[rgba(220,235,211,0.055)] p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#d4933d]">
                Key contribution
              </p>
              <p className="mt-3 text-sm leading-7 text-[#b8d1a8]">
                Built a foundation for environmental education at Sichuan University and helped
                connect academic research with public learning.
              </p>
            </div>
          </div>

          <div className="max-w-[760px]">
            <p className="editorial-kicker text-[#a8cc8a]">
              {founderEyebrow}
            </p>
            {founderLabel ? (
              <p className="mt-4 text-sm font-semibold uppercase tracking-[0.16em] text-[#d4933d]">
                {founderLabel}
              </p>
            ) : null}
            <h2 className="mt-3 font-serif text-[1.8rem] leading-[1.14] tracking-[-0.025em] text-white md:text-[2.35rem]">
              {founderHeading}
            </h2>

            <div className="mt-7 max-w-[680px] space-y-4 text-[0.98rem] leading-8 text-[#bfd4b4]">
              {founderParagraphs.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
            </div>

            <div className="mt-8 grid gap-3 border-t border-[rgba(168,204,138,0.16)] pt-8 sm:grid-cols-3">
              {PROFILE_HIGHLIGHTS.map((highlight) => (
                <p
                  key={highlight}
                  className="rounded-[18px] border border-[rgba(168,204,138,0.14)] bg-[rgba(220,235,211,0.055)] p-4 text-sm leading-6 text-[#d7e7ce]"
                >
                  {highlight}
                </p>
              ))}
            </div>

            <div className="mt-8 rounded-[24px] border border-[rgba(212,147,61,0.24)] bg-[rgba(212,147,61,0.08)] p-6">
              <p className="font-serif text-[1.25rem] text-white">
                {founder.question_heading?.trim() || FALLBACK_FOUNDER.question_heading}
              </p>
              <Link
                href={
                  founder.question_cta_link?.trim() ||
                  FALLBACK_FOUNDER.question_cta_link ||
                  "/contact"
                }
                className="mt-4 inline-flex items-center text-xs font-bold uppercase tracking-[0.16em] text-[#d4933d] transition-colors hover:text-[#f1b667]"
              >
                {founder.question_cta_label?.trim() ||
                  FALLBACK_FOUNDER.question_cta_label ||
                  "Connect With Us"}
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

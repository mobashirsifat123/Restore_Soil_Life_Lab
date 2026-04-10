/* eslint-disable @next/next/no-img-element */

import Link from "next/link";

import { getCmsPage } from "@/lib/cmsData";
import type {
  AboutCredential,
  AboutFounder,
  AboutIntroLegacy,
  AboutSections,
  CmsPage,
} from "@/lib/cmsTypes";

export const revalidate = 60;

const FALLBACK_FOUNDER: AboutFounder = {
  eyebrow: "Our Founder",
  label: "Dr. Lu Hongyan",
  name: "A soil scientist devoted to rebuilding living agricultural systems.",
  image_url: "/images/soil-scientist-hands.png",
  image_alt: "Scientist holding healthy living soil in both hands",
  paragraph_one:
    "For more than two decades, Bio Soil's scientific leadership has focused on turning complex soil biology into practical guidance that growers, consultants, and communities can actually apply in the field.",
  paragraph_two:
    "Our work centers on the living relationships between plants, fungi, bacteria, protozoa, nematodes, and organic matter. When those relationships are restored, degraded land can begin functioning like healthy soil again.",
  paragraph_three:
    "Everything we build, from education to diagnostics to software, is designed to help people understand that biology clearly and use it to regenerate the soils that sustain their region.",
  question_heading: "Have more questions?",
  question_cta_label: "Connect With Us",
  question_cta_link: "/contact",
};

const FALLBACK_CREDENTIALS: AboutCredential[] = [
  { text: "B.A., Biology and Chemistry" },
  { text: "M.S., Microbial Ecology" },
  { text: "Ph.D., Soil Microbiology" },
];

function normalizeFounder(
  founder: AboutFounder | undefined,
  intro: AboutIntroLegacy | undefined,
): AboutFounder {
  if (founder) {
    return { ...FALLBACK_FOUNDER, ...founder };
  }

  const paragraphs = intro?.paragraphs ?? [];
  return {
    ...FALLBACK_FOUNDER,
    eyebrow: intro?.kicker ?? FALLBACK_FOUNDER.eyebrow,
    name: intro?.heading ?? FALLBACK_FOUNDER.name,
    image_url: intro?.image_url ?? FALLBACK_FOUNDER.image_url,
    paragraph_one: paragraphs[0] ?? FALLBACK_FOUNDER.paragraph_one,
    paragraph_two: paragraphs[1] ?? FALLBACK_FOUNDER.paragraph_two,
    paragraph_three: paragraphs[2] ?? FALLBACK_FOUNDER.paragraph_three,
  };
}

export default async function AboutPage() {
  let page: CmsPage | null = null;
  let sections: AboutSections = {};

  try {
    const data = await getCmsPage("about");
    page = data?.page ?? null;
    sections = (data?.sections as AboutSections | undefined) ?? {};
  } catch {
    /* fallback */
  }

  const founder = normalizeFounder(sections.founder, sections.intro);
  const credentials = sections.founder_credentials?.length
    ? sections.founder_credentials
    : FALLBACK_CREDENTIALS;

  const heroKicker = page?.hero_kicker ?? "About";
  const heroHeading =
    page?.hero_heading ??
    "Our mission is to help people and organizations regenerate the soils that sustain their communities.";
  const heroSubheading =
    page?.hero_subheading ??
    "Bio Soil turns soil food web science into clear education, measurable diagnostics, and practical next steps for the people doing the work on the ground.";

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
    <div className="min-h-screen bg-[#f4efe4] text-[#1f2a1a]">
      <section className="content-auto relative overflow-hidden px-6 py-24 md:py-32">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute left-1/2 top-0 h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-[rgba(173,140,87,0.10)] blur-3xl" />
          <div className="absolute bottom-[-120px] left-[-60px] h-[320px] w-[320px] rounded-full bg-[rgba(92,116,77,0.10)] blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-[980px] text-center">
          <p className="text-[0.72rem] font-semibold uppercase tracking-[0.32em] text-[#6e7b5f]">
            {heroKicker}
          </p>
          <h1 className="mx-auto mt-6 max-w-[900px] font-serif text-[2.8rem] leading-[1.06] tracking-[-0.04em] text-[#1c2418] md:text-[4.6rem]">
            {heroHeading}
          </h1>
          <div className="mx-auto mt-8 h-px w-20 bg-[#c7ae82]" />
          <p className="mx-auto mt-8 max-w-[760px] text-[1.08rem] leading-9 text-[#5f6b56] md:text-[1.15rem]">
            {heroSubheading}
          </p>
        </div>
      </section>

      <section className="content-auto bg-[#fbf8f2] px-6 py-20 md:py-24">
        <div className="mx-auto grid max-w-[1180px] gap-14 lg:grid-cols-[minmax(0,420px)_minmax(0,1fr)] lg:items-start">
          <div className="relative">
            <div className="absolute inset-6 rounded-[30px] bg-[rgba(173,140,87,0.13)] blur-2xl" />
            <div className="relative overflow-hidden rounded-[34px] border border-[rgba(92,116,77,0.14)] bg-[#efe7d7] p-3 shadow-[0_22px_60px_rgba(39,49,32,0.12)]">
              <div className="overflow-hidden rounded-[28px] bg-[#d8ccb5]">
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
          </div>

          <div className="max-w-[680px]">
            <p className="text-[0.74rem] font-semibold uppercase tracking-[0.3em] text-[#6d7b60]">
              {founderEyebrow}
            </p>
            {founderLabel ? (
              <p className="mt-5 font-serif text-[1.9rem] leading-tight tracking-[-0.02em] text-[#24301d] md:text-[2.35rem]">
                {founderLabel}
              </p>
            ) : null}
            <h2 className="mt-3 font-serif text-[2.4rem] leading-[1.08] tracking-[-0.035em] text-[#1d2519] md:text-[3.35rem]">
              {founderHeading}
            </h2>

            <div className="mt-8 space-y-6 text-[1.02rem] leading-8 text-[#576453]">
              {founderParagraphs.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
            </div>

            {credentials.length ? (
              <div className="mt-8 space-y-3 border-t border-[rgba(92,116,77,0.14)] pt-8">
                {credentials.map((credential) => (
                  <p
                    key={credential.text}
                    className="text-[0.93rem] font-medium tracking-[0.02em] text-[#31402b]"
                  >
                    {credential.text}
                  </p>
                ))}
              </div>
            ) : null}

            <div className="mt-10 rounded-[28px] border border-[rgba(92,116,77,0.14)] bg-[#f4efe4] p-6 md:p-7">
              <p className="font-serif text-[1.4rem] text-[#1f2819]">
                {founder.question_heading?.trim() || FALLBACK_FOUNDER.question_heading}
              </p>
              <Link
                href={
                  founder.question_cta_link?.trim() ||
                  FALLBACK_FOUNDER.question_cta_link ||
                  "/contact"
                }
                className="mt-3 inline-flex items-center text-sm font-semibold uppercase tracking-[0.18em] text-[#4b6939] transition-colors hover:text-[#1d3318]"
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

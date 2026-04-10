import Link from "next/link";
import { getCmsPage } from "@/lib/cmsData";
import type {
  CmsPage,
  ScienceConcept,
  ScienceLevel,
  ScienceSections,
  StatTile,
} from "@/lib/cmsTypes";

export const revalidate = 60;

const FALLBACK_CONCEPTS = [
  {
    id: "soil-food-web",
    icon: "🕸️",
    title: "The Soil Food Web",
    subtitle: "Nature's Soil Operating System",
    body: "The soil food web is the interconnected community of organisms living in soil — bacteria, fungi, protozoa, nematodes, arthropods, earthworms, and more. Each plays a specific role in nutrient cycling, soil structure, and plant health. When this web is intact, plants thrive without chemical inputs.",
    detail:
      "A single tablespoon of healthy soil contains 1 billion bacteria, 120,000 fungi, and 25,000 protozoa — each essential.",
  },
  {
    id: "nutrient-cycling",
    icon: "♻️",
    title: "Nutrient Cycling",
    subtitle: "Plants control their own nutrition",
    body: "Plants exude sugars through their roots to attract bacteria and fungi. These microbes dissolve and immobilise nutrients. Protozoa and nematodes eat the bacteria and fungi, releasing nutrients directly in the root zone — in the exact form plants need, at the right time. No leaching. No waste.",
    detail:
      "Restored nutrient cycling has been linked to yield increases of up to 150% in the first growing season.",
  },
  {
    id: "carbon-sequestration",
    icon: "🌍",
    title: "Carbon Sequestration",
    subtitle: "Soil as the climate solution",
    body: "Plants absorb CO₂ during photosynthesis and invest approximately 40% as root exudates to feed soil microorganisms. These organisms build stable organic compounds — humus and glomalin — that lock carbon into the soil for decades. Scientists estimate that restoring the world's soils could halt and reverse climate change within 15–20 years.",
    detail:
      "Biological agriculture can sequester 2–5 tonnes of carbon per hectare per year — far exceeding industrial tree planting.",
  },
  {
    id: "suppress-pests-disease",
    icon: "🛡️",
    title: "Pest & Disease Suppression",
    subtitle: "Built-in natural protection",
    body: "A complete soil food web naturally suppresses pathogens and pests. Fungal networks produce antibiotic compounds. Bacterial films coat root surfaces, blocking pathogen attachment. Predatory nematodes control harmful pest populations. The result: crops grown in biologically active soil have far lower disease and pest pressure — without pesticides.",
    detail: "Farmers report up to 100% reduction in pesticide use after restoring soil biology.",
  },
  {
    id: "weed-suppression",
    icon: "🌾",
    title: "Weed Suppression",
    subtitle: "Biology outcompetes weeds",
    body: "Weeds are indicators of disturbed or depleted soil. They colonise biological vacuums left by degraded growing conditions. When soil biology is restored, desirable plant communities competitive advantage increases dramatically. Biology — not herbicide — becomes the primary weed management system.",
    detail: "Cover crop diversity + biological soil management can reduce weed pressure by 60–80%.",
  },
  {
    id: "structure-formation",
    icon: "⛰️",
    title: "Soil Structure Formation",
    subtitle: "Building soil from within",
    body: "Bacteria produce sticky polysaccharides that bind soil particles into aggregates. Fungal hyphae create a physical mesh that reinforces aggregate stability. Earthworms produce castings that dramatically improve water infiltration and aeration. This structured soil resists erosion, holds moisture, and supports deep root penetration.",
    detail:
      "Biologically active soil holds 3× more water than compacted or chemically treated soil of the same texture.",
  },
];

const FALLBACK_FOOD_WEB_LEVELS = [
  {
    level: 1,
    name: "Primary Producers",
    members: "Plants, Algae",
    color: "#3a8c2f",
    description: "Fix energy from sunlight, feed the web with root exudates",
  },
  {
    level: 2,
    name: "Primary Consumers",
    members: "Bacteria, Fungi, Root Feeders",
    color: "#5a7c2f",
    description: "Break down organic matter, immobilise nutrients",
  },
  {
    level: 3,
    name: "Secondary Consumers",
    members: "Protozoa, Nematodes, Microarthropods",
    color: "#8aaa3a",
    description: "Eat bacteria and fungi, release nutrients in plant-available forms",
  },
  {
    level: 4,
    name: "Tertiary Consumers",
    members: "Predatory Nematodes, Mites, Spiders",
    color: "#b9933d",
    description: "Regulate lower trophic levels, prevent population imbalances",
  },
  {
    level: 5,
    name: "Higher-Order Predators",
    members: "Earthworms, Centipedes, Beetles",
    color: "#d4933d",
    description: "Redistribute organic matter, aerate and structure soil",
  },
  {
    level: 6,
    name: "Apex Organisms",
    members: "Mammals, Birds, Reptiles",
    color: "#b97849",
    description: "Long-range redistribution of nutrients and biology",
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

  const concepts: ScienceConcept[] = sections.concepts ?? FALLBACK_CONCEPTS;
  const foodWebLevels: ScienceLevel[] = sections.food_web_levels ?? FALLBACK_FOOD_WEB_LEVELS;
  const stats: StatTile[] = sections.stats ?? [
    { n: "1B+", label: "Bacteria per teaspoon of soil" },
    { n: "120,000", label: "Fungal strands per teaspoon" },
    { n: "40%", label: "Of plant photosynthate invested in soil" },
    { n: "15–20yr", label: "Timeline to halt climate change via soil" },
  ];

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

      {/* Food web pyramid */}
      <section className="content-auto bg-[#f5efdf] px-6 py-20">
        <div className="mx-auto max-w-[900px]">
          <div className="text-center mb-12">
            <p className="editorial-kicker text-[#3a5c2f] mb-3">The trophic structure</p>
            <h2 className="font-serif text-[2.2rem] text-[#1e3318] tracking-[-0.03em]">
              The Six Levels of the Soil Food Web
            </h2>
          </div>
          <div className="space-y-3">
            {foodWebLevels.map((level: ScienceLevel) => (
              <div
                key={level.level}
                className="flex gap-5 items-start rounded-2xl border border-[rgba(58,92,47,0.10)] bg-white p-5 card-hover"
              >
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0 mt-0.5"
                  style={{ backgroundColor: level.color }}
                >
                  {level.level}
                </div>
                <div className="flex-1">
                  <div className="flex flex-wrap items-baseline gap-3 mb-1">
                    <span className="font-serif text-[1.1rem] text-[#1e3318]">{level.name}</span>
                    <span className="text-xs tag-pill">{level.members}</span>
                  </div>
                  <p className="text-sm text-[#5a6e50] leading-6">{level.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Concepts */}
      <section className="content-auto bg-cream-section px-6 py-20">
        <div className="mx-auto max-w-[1100px]">
          <div className="text-center mb-14">
            <p className="editorial-kicker text-[#3a5c2f] mb-3">Core mechanisms</p>
            <h2 className="font-serif text-[2.4rem] text-[#1e3318] tracking-[-0.03em]">
              Key Scientific Concepts
            </h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6 stagger">
            {concepts.map((concept: ScienceConcept) => (
              <div
                key={concept.id}
                id={concept.id}
                className="card-hover rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-8"
              >
                <span className="text-3xl block mb-4">{concept.icon}</span>
                <p className="editorial-kicker text-[#3a5c2f] mb-1">{concept.subtitle}</p>
                <h3 className="font-serif text-[1.5rem] text-[#1e3318] mb-3">{concept.title}</h3>
                <p className="text-[#4a5e40] leading-7 mb-5 text-sm">{concept.body}</p>
                <div className="rounded-2xl bg-[#f0f7ed] border border-[rgba(58,92,47,0.1)] px-5 py-4">
                  <p className="text-[#3a5c2f] text-xs font-semibold uppercase tracking-[0.14em] mb-1">
                    Key Finding
                  </p>
                  <p className="text-sm text-[#4a5e40] italic">{concept.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="content-auto bg-[#3a5c2f] px-6 py-14">
        <div className="mx-auto max-w-[1000px] grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map((s: StatTile) => (
            <div key={s.label}>
              <p className="font-serif text-[2.4rem] font-bold text-[#d4933d] leading-none">
                {s.n}
              </p>
              <p className="text-[#b8d4a0] text-sm mt-2 leading-5">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="content-auto bg-[#f5efdf] px-6 py-20 text-center">
        <div className="mx-auto max-w-[600px]">
          <h2 className="font-serif text-[2.2rem] text-[#1e3318] mb-4 tracking-[-0.03em]">
            Ready to measure your soil food web?
          </h2>
          <p className="text-[#4a5e40] leading-7 mb-8">
            Use our free SilkSoil to get a biological baseline of your own soil — with component
            scores, F:B ratio, and restoration recommendations.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/silksoil"
              className="button-glow rounded-full bg-[#3a5c2f] px-7 py-4 font-semibold text-white hover:bg-[#1e3318] transition-colors shadow-md"
            >
              Open SilkSoil
            </Link>
            <Link
              href="/blog"
              className="button-glow rounded-full border border-[rgba(58,92,47,0.25)] px-7 py-4 font-semibold text-[#3a5c2f] hover:bg-[rgba(58,92,47,0.06)] transition-colors"
            >
              Read the Science Blog
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { InlineEditor } from "@/components/admin/InlineEditor";
import { SectionEditor } from "@/components/admin/SectionEditor";
import { cmsApi } from "@/lib/cmsApi";
import type {
  AboutCredential,
  AboutFounder,
  AboutIntroLegacy,
  AboutSections,
  CmsPage,
  CmsPageResponse,
} from "@/lib/cmsTypes";

const DEFAULT_FOUNDER: AboutFounder = {
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

const DEFAULT_CREDENTIALS: AboutCredential[] = [
  { text: "B.A., Biology and Chemistry" },
  { text: "M.S., Microbial Ecology" },
  { text: "Ph.D., Soil Microbiology" },
];

function normalizeFounder(
  founder: AboutFounder | undefined,
  intro: AboutIntroLegacy | undefined,
): AboutFounder {
  if (founder) {
    return { ...DEFAULT_FOUNDER, ...founder };
  }

  const paragraphs = intro?.paragraphs ?? [];
  return {
    ...DEFAULT_FOUNDER,
    eyebrow: intro?.kicker ?? DEFAULT_FOUNDER.eyebrow,
    name: intro?.heading ?? DEFAULT_FOUNDER.name,
    image_url: intro?.image_url ?? DEFAULT_FOUNDER.image_url,
    paragraph_one: paragraphs[0] ?? DEFAULT_FOUNDER.paragraph_one,
    paragraph_two: paragraphs[1] ?? DEFAULT_FOUNDER.paragraph_two,
    paragraph_three: paragraphs[2] ?? DEFAULT_FOUNDER.paragraph_three,
  };
}

async function saveVoid(action: Promise<unknown>): Promise<void> {
  await action;
}

export default function AdminAboutPage() {
  const [pageData, setPageData] = useState<CmsPageResponse<AboutSections> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadPage() {
    setLoading(true);
    try {
      const data = (await cmsApi.getPage("about")) as CmsPageResponse<AboutSections>;
      setPageData(data);
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to load about page data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadPage();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Loading about page content"
          description="Fetching the current about page sections and founder spotlight data."
        />
      </div>
    );
  }

  if (!pageData) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="About page content is unavailable"
          description={error ?? "The about page could not be loaded from the CMS."}
          variant="error"
          actionLabel="Retry"
          onAction={() => void loadPage()}
        />
      </div>
    );
  }

  const { page, sections } = pageData as { page: CmsPage; sections: AboutSections };
  const founder = normalizeFounder(sections.founder, sections.intro);
  const credentials = sections.founder_credentials?.length
    ? sections.founder_credentials
    : DEFAULT_CREDENTIALS;

  return (
    <div className="max-w-5xl p-8">
      <div className="mb-8">
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-[#5a8050]">
          About
        </p>
        <h1 className="font-serif text-3xl text-white">Edit About Page</h1>
      </div>

      <div className="space-y-6">
        <InlineEditor
          title="Hero"
          fields={[
            { key: "title", label: "Browser Tab Title" },
            { key: "meta_description", label: "Meta Description", multiline: true },
            { key: "hero_kicker", label: "Eyebrow" },
            { key: "hero_heading", label: "Main Heading", multiline: true },
            { key: "hero_subheading", label: "Supporting Copy", multiline: true },
          ]}
          initialValues={{
            title: page.title ?? "",
            meta_description: page.meta_description ?? "",
            hero_kicker: page.hero_kicker ?? "",
            hero_heading: page.hero_heading ?? "",
            hero_subheading: page.hero_subheading ?? "",
          }}
          onSave={(vals) => saveVoid(cmsApi.updatePage("about", vals))}
        />

        <InlineEditor
          title="Founder Spotlight"
          fields={[
            { key: "eyebrow", label: "Section Eyebrow" },
            { key: "label", label: "Founder Name / Label" },
            { key: "name", label: "Large Founder Heading", multiline: true },
            { key: "image_url", label: "Portrait Image URL" },
            { key: "image_alt", label: "Portrait Alt Text" },
            { key: "paragraph_one", label: "Paragraph One", multiline: true },
            { key: "paragraph_two", label: "Paragraph Two", multiline: true },
            { key: "paragraph_three", label: "Paragraph Three", multiline: true },
            { key: "question_heading", label: "Question Prompt" },
            { key: "question_cta_label", label: "Question CTA Label" },
            { key: "question_cta_link", label: "Question CTA Link" },
          ]}
          initialValues={{
            eyebrow: founder.eyebrow ?? "",
            label: founder.label ?? "",
            name: founder.name ?? "",
            image_url: founder.image_url ?? "",
            image_alt: founder.image_alt ?? "",
            paragraph_one: founder.paragraph_one ?? "",
            paragraph_two: founder.paragraph_two ?? "",
            paragraph_three: founder.paragraph_three ?? "",
            question_heading: founder.question_heading ?? "",
            question_cta_label: founder.question_cta_label ?? "",
            question_cta_link: founder.question_cta_link ?? "",
          }}
          onSave={(vals) =>
            saveVoid(cmsApi.updateSection("about", "founder", { ...founder, ...vals }))
          }
        />

        <SectionEditor
          title="Founder Credentials"
          items={credentials}
          fields={[{ key: "text", label: "Credential / Qualification" }]}
          onSave={(items) => saveVoid(cmsApi.updateSection("about", "founder_credentials", items))}
          addLabel="Add Credential"
        />
      </div>
    </div>
  );
}

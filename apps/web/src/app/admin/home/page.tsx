"use client";

import { useEffect, useState } from "react";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { InlineEditor } from "@/components/admin/InlineEditor";
import { SectionEditor } from "@/components/admin/SectionEditor";
import { cmsApi } from "@/lib/cmsApi";
import type { CmsPage, CmsPageResponse, HomeSections } from "@/lib/cmsTypes";

async function saveVoid(action: Promise<unknown>): Promise<void> {
  await action;
}

export default function AdminHomePage() {
  const [pageData, setPageData] = useState<CmsPageResponse<HomeSections> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadPage() {
    setLoading(true);
    try {
      const data = (await cmsApi.getPage("home")) as CmsPageResponse<HomeSections>;
      setPageData(data);
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to load homepage content.");
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
          title="Loading homepage content"
          description="Pulling the current homepage structure from the CMS so you can edit it safely."
        />
      </div>
    );
  }

  if (!pageData) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Homepage content is unavailable"
          description={
            error ??
            "The CMS did not return homepage content. This usually means the API or database is degraded."
          }
          variant="error"
          actionLabel="Retry"
          onAction={() => void loadPage()}
        />
      </div>
    );
  }

  const { page, sections } = pageData as { page: CmsPage; sections: HomeSections };

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <p className="text-[#5a8050] text-xs font-semibold uppercase tracking-[0.2em] mb-2">
          Homepage
        </p>
        <h1 className="font-serif text-3xl text-white">Edit Homepage</h1>
      </div>

      <div className="space-y-6">
        {/* Hero */}
        <InlineEditor
          title="🏠 Hero Section"
          fields={[
            { key: "title", label: "Browser Tab Title" },
            { key: "meta_description", label: "Meta Description (SEO)", multiline: true },
            { key: "hero_kicker", label: "Kicker (small text above heading)" },
            { key: "hero_heading", label: "Main Heading (H1)", multiline: true },
            { key: "hero_subheading", label: "Subheading Paragraph", multiline: true },
            { key: "hero_image_url", label: "Hero Image URL" },
          ]}
          initialValues={{
            title: page.title ?? "",
            meta_description: page.meta_description ?? "",
            hero_kicker: page.hero_kicker ?? "",
            hero_heading: page.hero_heading ?? "",
            hero_subheading: page.hero_subheading ?? "",
            hero_image_url: page.hero_image_url ?? "",
          }}
          onSave={(vals) => saveVoid(cmsApi.updatePage("home", vals))}
        />

        {/* Problems */}
        <SectionEditor
          title="🌿 Problem Cards (6 cards)"
          items={sections.problems ?? []}
          fields={[
            { key: "icon", label: "Icon (emoji)" },
            { key: "title", label: "Title" },
            { key: "subtitle", label: "Subtitle / Badge" },
            { key: "body", label: "Body text", multiline: true },
            { key: "link", label: "Link URL" },
          ]}
          onSave={(items) => saveVoid(cmsApi.updateSection("home", "problems", items))}
        />

        {/* Stats */}
        <SectionEditor
          title="📊 Stats Strip (4 tiles)"
          items={sections.stats ?? []}
          fields={[
            { key: "number", label: "Number / Stat" },
            { key: "label", label: "Label" },
            { key: "sub", label: "Sub label" },
          ]}
          onSave={(items) => saveVoid(cmsApi.updateSection("home", "stats", items))}
        />

        {/* Testimonials */}
        <SectionEditor
          title="💬 Testimonials"
          items={sections.testimonials ?? []}
          fields={[
            { key: "quote", label: "Quote", multiline: true },
            { key: "author", label: "Author name" },
            { key: "role", label: "Author role / location" },
          ]}
          onSave={(items) => saveVoid(cmsApi.updateSection("home", "testimonials", items))}
        />

        {/* Calculator spotlight */}
        {sections.calculator_spotlight && (
          <InlineEditor
            title="📊 Calculator Spotlight Section"
            fields={[
              { key: "kicker", label: "Kicker label" },
              { key: "heading", label: "Heading" },
              { key: "body", label: "Body text", multiline: true },
              { key: "cta_text", label: "CTA Button text" },
              { key: "cta_link", label: "CTA Link URL" },
              { key: "image_url", label: "Image URL" },
            ]}
            initialValues={sections.calculator_spotlight}
            onSave={(vals) => {
              const updated = { ...sections.calculator_spotlight, ...vals };
              return saveVoid(cmsApi.updateSection("home", "calculator_spotlight", updated));
            }}
          />
        )}

        {/* About section */}
        {sections.about_section && (
          <InlineEditor
            title="🌱 About Section"
            fields={[
              { key: "kicker", label: "Kicker" },
              { key: "heading", label: "Heading" },
              { key: "body1", label: "Paragraph 1", multiline: true },
              { key: "body2", label: "Paragraph 2", multiline: true },
              { key: "video_caption", label: "Video caption" },
            ]}
            initialValues={sections.about_section}
            onSave={(vals) => {
              const updated = { ...sections.about_section, ...vals };
              return saveVoid(cmsApi.updateSection("home", "about_section", updated));
            }}
          />
        )}
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { InlineEditor } from "@/components/admin/InlineEditor";
import { SectionEditor } from "@/components/admin/SectionEditor";
import { cmsApi } from "@/lib/cmsApi";
import type { CmsPage, CmsPageResponse, ScienceSections } from "@/lib/cmsTypes";

async function saveVoid(action: Promise<unknown>): Promise<void> {
  await action;
}

export default function AdminSciencePage() {
  const [pageData, setPageData] = useState<CmsPageResponse<ScienceSections> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadPage() {
    setLoading(true);
    try {
      const data = (await cmsApi.getPage("science")) as CmsPageResponse<ScienceSections>;
      setPageData(data);
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to load science page data.");
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
          title="Loading science page content"
          description="Fetching the science page structure so edits stay grounded in the current CMS state."
        />
      </div>
    );
  }

  if (!pageData) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Science page content is unavailable"
          description={error ?? "The science page could not be loaded from the CMS."}
          variant="error"
          actionLabel="Retry"
          onAction={() => void loadPage()}
        />
      </div>
    );
  }

  const { page, sections } = pageData as { page: CmsPage; sections: ScienceSections };

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <p className="text-[#5a8050] text-xs font-semibold uppercase tracking-[0.2em] mb-2">
          Science
        </p>
        <h1 className="font-serif text-3xl text-white">Edit Science Page</h1>
      </div>

      <div className="space-y-6">
        {/* Hero */}
        <InlineEditor
          title="🔬 Hero Section"
          fields={[
            { key: "title", label: "Browser Tab Title" },
            { key: "meta_description", label: "Meta Description (SEO)", multiline: true },
            { key: "hero_kicker", label: "Kicker" },
            { key: "hero_heading", label: "Main Heading (H1)", multiline: true },
            { key: "hero_subheading", label: "Subheading", multiline: true },
          ]}
          initialValues={{
            title: page.title ?? "",
            meta_description: page.meta_description ?? "",
            hero_kicker: page.hero_kicker ?? "",
            hero_heading: page.hero_heading ?? "",
            hero_subheading: page.hero_subheading ?? "",
          }}
          onSave={(vals) => saveVoid(cmsApi.updatePage("science", vals))}
        />

        {/* Food web levels */}
        <SectionEditor
          title="🕸️ Food Web Trophic Levels (6 rows)"
          items={sections.food_web_levels ?? []}
          fields={[
            { key: "level", label: "Level number", type: "number" },
            { key: "name", label: "Level name" },
            { key: "members", label: "Members (comma-separated)" },
            { key: "color", label: "Colour hex (e.g. #3a8c2f)" },
            { key: "description", label: "Description", multiline: true },
          ]}
          onSave={(items) => saveVoid(cmsApi.updateSection("science", "food_web_levels", items))}
        />

        {/* Key concepts */}
        <SectionEditor
          title="💡 Key Concept Cards (6 cards)"
          items={sections.concepts ?? []}
          fields={[
            { key: "icon", label: "Icon (emoji)" },
            { key: "title", label: "Title" },
            { key: "subtitle", label: "Subtitle" },
            { key: "body", label: "Body text", multiline: true },
            { key: "detail", label: "Detail stat / callout", multiline: true },
          ]}
          onSave={(items) => saveVoid(cmsApi.updateSection("science", "concepts", items))}
          addLabel="Add Concept Card"
        />

        {/* Stats */}
        <SectionEditor
          title="📊 Scientific Stats (4 tiles)"
          items={sections.stats ?? []}
          fields={[
            { key: "n", label: "Stat value" },
            { key: "label", label: "Label" },
          ]}
          onSave={(items) => saveVoid(cmsApi.updateSection("science", "stats", items))}
        />
      </div>
    </div>
  );
}

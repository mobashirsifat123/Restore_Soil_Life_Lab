"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { cmsApi } from "@/lib/cmsApi";
import type { BlogPostDetail } from "@/lib/cmsTypes";

const CATEGORIES = ["Science", "Case Studies", "Updates", "Events", "Community"];

export default function EditBlogPostPage() {
  const params = useParams();
  const postId = params.id as string;

  const [form, setForm] = useState<BlogPostDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cmsApi
      .getPost(postId)
      .then(setForm)
      .finally(() => setLoading(false));
  }, [postId]);

  function setField(key: string, value: unknown) {
    setForm((current) => (current ? { ...current, [key]: value } : current));
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await cmsApi.updatePost(postId, { ...form, publish: undefined });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : "Failed to save post.");
    } finally {
      setSaving(false);
    }
  }

  async function handlePublishToggle() {
    if (!form) return;
    const willPublish = !form.published_at;
    await cmsApi.updatePost(postId, { publish: willPublish });
    setForm((current) =>
      current
        ? { ...current, published_at: willPublish ? new Date().toISOString() : null }
        : current,
    );
  }

  if (loading) return <div className="p-8 text-[#5a8050]">Loading…</div>;
  if (!form) return <div className="p-8 text-red-400">Post not found.</div>;

  return (
    <div className="p-8 max-w-4xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <p className="text-[#5a8050] text-xs font-semibold uppercase tracking-[0.2em] mb-2">
            Blog → Edit
          </p>
          <h1 className="font-serif text-3xl text-white truncate max-w-[500px]">
            {form.title || "Untitled"}
          </h1>
        </div>
        <button
          onClick={handlePublishToggle}
          className={`px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${
            form.published_at
              ? "bg-[rgba(239,68,68,0.15)] text-red-400 hover:bg-[rgba(239,68,68,0.25)]"
              : "bg-[rgba(22,163,74,0.15)] text-[#4ade80] hover:bg-[rgba(22,163,74,0.25)]"
          }`}
        >
          {form.published_at ? "Unpublish" : "Publish"}
        </button>
      </div>

      <div className="space-y-5">
        <div className="grid grid-cols-2 gap-4 rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
          <div className="col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Title
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.title ?? ""}
              onChange={(e) => setField("title", e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Slug
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.slug ?? ""}
              onChange={(e) => setField("slug", e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Category
            </label>
            <select
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.category ?? ""}
              onChange={(e) => setField("category", e.target.value)}
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Author
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.author ?? ""}
              onChange={(e) => setField("author", e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Read time (min)
            </label>
            <input
              type="number"
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.read_time_minutes ?? 5}
              onChange={(e) => setField("read_time_minutes", Number(e.target.value))}
            />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Cover Image URL
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.cover_image_url ?? ""}
              onChange={(e) => setField("cover_image_url", e.target.value)}
            />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Excerpt
            </label>
            <textarea
              rows={3}
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm resize-y focus:outline-none focus:border-[#a8cc8a]"
              value={form.excerpt ?? ""}
              onChange={(e) => setField("excerpt", e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="featured"
              checked={form.is_featured ?? false}
              onChange={(e) => setField("is_featured", e.target.checked)}
              className="w-4 h-4 accent-[#a8cc8a]"
            />
            <label htmlFor="featured" className="text-sm text-[#7a9a6a]">
              Featured post
            </label>
          </div>
        </div>

        <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
          <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-3">
            Body (Markdown)
          </label>
          <textarea
            rows={24}
            className="w-full bg-[rgba(0,0,0,0.2)] border border-[rgba(168,204,138,0.1)] rounded-xl px-4 py-3 text-white text-sm font-mono resize-y focus:outline-none focus:border-[#a8cc8a] transition-colors"
            value={form.body_markdown ?? ""}
            onChange={(e) => setField("body_markdown", e.target.value)}
          />
        </div>

        {error && <p className="text-red-400 text-sm">✗ {error}</p>}
        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-5 py-2.5 rounded-xl bg-[#3a5c2f] hover:bg-[#4a7a3a] text-white text-sm font-semibold transition-colors disabled:opacity-50"
          >
            {saving ? "Saving…" : "Save Changes"}
          </button>
          {saved && <span className="text-sm text-[#a8cc8a] self-center">✓ Saved</span>}
        </div>
      </div>
    </div>
  );
}

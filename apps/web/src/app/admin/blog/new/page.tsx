"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { cmsApi } from "@/lib/cmsApi";

const CATEGORIES = ["Science", "Case Studies", "Updates", "Events", "Community"];

type NewBlogPostForm = {
  title: string;
  slug: string;
  category: string;
  author: string;
  excerpt: string;
  body_markdown: string;
  cover_image_url: string;
  is_featured: boolean;
  read_time_minutes: number;
  publish: boolean;
};

export default function NewBlogPostPage() {
  const router = useRouter();
  const [form, setForm] = useState<NewBlogPostForm>({
    title: "",
    slug: "",
    category: "Science",
    author: "",
    excerpt: "",
    body_markdown: "",
    cover_image_url: "",
    is_featured: false,
    read_time_minutes: 5,
    publish: false,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function setField<K extends keyof NewBlogPostForm>(key: K, value: NewBlogPostForm[K]) {
    setForm((current) => {
      const next = { ...current, [key]: value };
      if (key === "title" && !current.slug) {
        next.slug = String(value)
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-|-$/g, "");
      }
      return next;
    });
  }

  async function handleSave(publish = false) {
    setSaving(true);
    setError(null);
    try {
      const post = await cmsApi.createPost({ ...form, publish });
      router.push(`/admin/blog/${post.id}`);
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : "Failed to create post.");
      setSaving(false);
    }
  }

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <p className="text-[#5a8050] text-xs font-semibold uppercase tracking-[0.2em] mb-2">Blog</p>
        <h1 className="font-serif text-3xl text-white">New Post</h1>
      </div>

      <div className="space-y-5">
        {/* Meta */}
        <div className="grid grid-cols-2 gap-4 rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
          <div className="col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Title
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.title}
              onChange={(e) => setField("title", e.target.value)}
              placeholder="Post title…"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Slug (URL)
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.slug}
              onChange={(e) => setField("slug", e.target.value)}
              placeholder="post-url-slug"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Category
            </label>
            <select
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.category}
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
              value={form.author}
              onChange={(e) => setField("author", e.target.value)}
              placeholder="Author name"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Read time (minutes)
            </label>
            <input
              type="number"
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.read_time_minutes}
              onChange={(e) => setField("read_time_minutes", Number(e.target.value))}
            />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Cover Image URL
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={form.cover_image_url}
              onChange={(e) => setField("cover_image_url", e.target.value)}
              placeholder="/images/…"
            />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Excerpt (short summary)
            </label>
            <textarea
              rows={3}
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm resize-y focus:outline-none focus:border-[#a8cc8a]"
              value={form.excerpt}
              onChange={(e) => setField("excerpt", e.target.value)}
              placeholder="Short excerpt for card view…"
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="featured"
              checked={form.is_featured}
              onChange={(e) => setField("is_featured", e.target.checked)}
              className="w-4 h-4 accent-[#a8cc8a]"
            />
            <label htmlFor="featured" className="text-sm text-[#7a9a6a]">
              Featured post (shown on homepage)
            </label>
          </div>
        </div>

        {/* Body */}
        <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
          <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-3">
            Body (Markdown)
          </label>
          <textarea
            rows={20}
            className="w-full bg-[rgba(0,0,0,0.2)] border border-[rgba(168,204,138,0.1)] rounded-xl px-4 py-3 text-white text-sm font-mono resize-y focus:outline-none focus:border-[#a8cc8a] transition-colors"
            value={form.body_markdown}
            onChange={(e) => setField("body_markdown", e.target.value)}
            placeholder="# Post Title&#10;&#10;Write your post in Markdown…"
          />
          <p className="mt-2 text-xs text-[#3a5030]">
            Supports full Markdown: # headings, **bold**, *italic*, - lists, [links](url),
            ![images](url)
          </p>
        </div>

        {/* Actions */}
        {error && <p className="text-red-400 text-sm">✗ {error}</p>}
        <div className="flex gap-3">
          <button
            onClick={() => handleSave(false)}
            disabled={saving}
            className="px-5 py-2.5 rounded-xl border border-[rgba(168,204,138,0.2)] text-[#a8cc8a] text-sm font-semibold hover:bg-[rgba(58,92,47,0.2)] transition-colors disabled:opacity-50"
          >
            Save as Draft
          </button>
          <button
            onClick={() => handleSave(true)}
            disabled={saving}
            className="px-5 py-2.5 rounded-xl bg-[#3a5c2f] hover:bg-[#4a7a3a] text-white text-sm font-semibold transition-colors disabled:opacity-50"
          >
            {saving ? "Publishing…" : "Publish Now"}
          </button>
        </div>
      </div>
    </div>
  );
}

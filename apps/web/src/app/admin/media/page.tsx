"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { cmsApi } from "@/lib/cmsApi";
import type { MediaAsset } from "@/lib/cmsTypes";

export default function AdminMediaPage() {
  const [assets, setAssets] = useState<MediaAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const [urlInput, setUrlInput] = useState("");
  const [altInput, setAltInput] = useState("");
  const [filenameInput, setFilenameInput] = useState("");

  async function reload() {
    setLoading(true);
    try {
      const data = await cmsApi.listMedia();
      setAssets(data);
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to load media library.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reload();
  }, []);

  async function handleAddUrl() {
    if (!urlInput.trim()) return;
    setUploading(true);
    setError(null);
    try {
      await cmsApi.createMedia({
        url: urlInput,
        filename: filenameInput || urlInput.split("/").pop() || "image",
        alt_text: altInput,
        mime_type: "image/*",
      });
      setUrlInput("");
      setAltInput("");
      setFilenameInput("");
      await reload();
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : "Failed to add media.");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id: string, name: string) {
    if (!confirm(`Remove "${name}" from the media library?`)) return;
    await cmsApi.deleteMedia(id);
    await reload();
  }

  function copyUrl(url: string) {
    navigator.clipboard.writeText(url);
    setCopied(url);
    setTimeout(() => setCopied(null), 1500);
  }

  if (loading) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Loading media library"
          description="Gathering shared site imagery and uploaded assets."
        />
      </div>
    );
  }

  if (error && assets.length === 0) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Media library is unavailable"
          description={error}
          variant="error"
          actionLabel="Retry"
          onAction={() => void reload()}
        />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-8">
        <p className="text-[#5a8050] text-xs font-semibold uppercase tracking-[0.2em] mb-2">
          Media
        </p>
        <h1 className="font-serif text-3xl text-white">Media Library</h1>
        <p className="text-[#5a7050] text-sm mt-1">{assets.length} assets registered</p>
      </div>

      {/* Add by URL */}
      <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6 mb-8">
        <h2 className="font-serif text-lg text-white mb-4">Register Image by URL</h2>
        <p className="text-xs text-[#5a7050] mb-4">
          Paste a URL to any public image (Supabase Storage, CDN, etc.) to add it to the library.
        </p>
        <div className="grid grid-cols-3 gap-3 mb-3">
          <div className="col-span-3">
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Image URL
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://… or /images/…"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Filename
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={filenameInput}
              onChange={(e) => setFilenameInput(e.target.value)}
              placeholder="my-image.jpg"
            />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              Alt text (accessibility)
            </label>
            <input
              className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a]"
              value={altInput}
              onChange={(e) => setAltInput(e.target.value)}
              placeholder="Description of image…"
            />
          </div>
        </div>
        {error && <p className="text-red-400 text-sm mb-3">✗ {error}</p>}
        <button
          onClick={handleAddUrl}
          disabled={uploading || !urlInput.trim()}
          className="px-5 py-2.5 rounded-xl bg-[#3a5c2f] hover:bg-[#4a7a3a] text-white text-sm font-semibold transition-colors disabled:opacity-50"
        >
          {uploading ? "Adding…" : "Add to Library"}
        </button>
      </div>

      {/* Grid */}
      {assets.length === 0 ? (
        <div className="text-center py-16 text-[#5a7050]">
          No media assets yet. Add images above.
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {assets.map((a) => (
            <div
              key={a.id}
              className="group rounded-2xl border border-[rgba(168,204,138,0.1)] bg-[rgba(255,255,255,0.03)] overflow-hidden hover:border-[rgba(168,204,138,0.25)] transition-all"
            >
              <div className="aspect-video bg-[rgba(0,0,0,0.3)] flex items-center justify-center overflow-hidden">
                <div className="relative h-full w-full">
                  <Image
                    src={a.url}
                    alt={a.alt_text || a.filename}
                    fill
                    className="object-cover"
                    unoptimized
                  />
                </div>
              </div>
              <div className="p-3">
                <p className="text-white text-xs font-medium truncate">{a.filename}</p>
                <p className="text-[#5a7050] text-xs mt-0.5 truncate">
                  {a.alt_text || "No alt text"}
                </p>
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => copyUrl(a.url)}
                    className="flex-1 text-xs py-1.5 rounded-lg border border-[rgba(168,204,138,0.15)] text-[#a8cc8a] hover:bg-[rgba(58,92,47,0.2)] transition-colors"
                  >
                    {copied === a.url ? "✓ Copied" : "Copy URL"}
                  </button>
                  <button
                    onClick={() => handleDelete(a.id, a.filename)}
                    className="text-xs px-2 py-1.5 rounded-lg text-red-500/50 hover:text-red-400 hover:bg-[rgba(239,68,68,0.1)] transition-colors"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

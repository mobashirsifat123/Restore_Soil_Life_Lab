"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { cmsApi } from "@/lib/cmsApi";
import type { BlogPostSummary } from "@/lib/cmsTypes";

type Post = BlogPostSummary;

export default function AdminBlogPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadPosts() {
    setLoading(true);
    try {
      const result = await cmsApi.listPosts(true);
      setPosts(result);
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to load blog posts.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadPosts();
  }, []);

  async function handleDelete(id: string, title: string) {
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;
    setDeleting(id);
    try {
      await cmsApi.deletePost(id);
      await loadPosts();
    } finally {
      setDeleting(null);
    }
  }

  async function handleTogglePublish(post: Post) {
    await cmsApi.updatePost(post.id, { publish: !post.published_at });
    await loadPosts();
  }

  if (loading) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Loading blog posts"
          description="Fetching all draft and published articles from the CMS."
        />
      </div>
    );
  }

  if (error && posts.length === 0) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Blog posts are unavailable"
          description={error}
          variant="error"
          actionLabel="Retry"
          onAction={() => void loadPosts()}
        />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl">
      <div className="flex items-start justify-between mb-8">
        <div>
          <p className="text-[#5a8050] text-xs font-semibold uppercase tracking-[0.2em] mb-2">
            Blog
          </p>
          <h1 className="font-serif text-3xl text-white">Blog Posts</h1>
          <p className="text-[#5a7050] text-sm mt-1">{posts.length} posts total</p>
        </div>
        <Link
          href="/admin/blog/new"
          className="px-5 py-2.5 rounded-xl bg-[#3a5c2f] hover:bg-[#4a7a3a] text-white text-sm font-semibold transition-colors"
        >
          + New Post
        </Link>
      </div>

      <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[rgba(168,204,138,0.08)]">
              {["Title", "Category", "Author", "Status", "Featured", "Actions"].map((h) => (
                <th
                  key={h}
                  className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-[#5a8050]"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {posts.map((post, i) => (
              <tr
                key={post.id}
                className={`border-b border-[rgba(168,204,138,0.06)] hover:bg-[rgba(255,255,255,0.02)] transition-colors ${i % 2 === 0 ? "" : "bg-[rgba(255,255,255,0.01)]"}`}
              >
                <td className="px-4 py-3">
                  <p className="text-white text-sm font-medium truncate max-w-[240px]">
                    {post.title}
                  </p>
                  <p className="text-[#5a7050] text-xs mt-0.5">/{post.slug}</p>
                </td>
                <td className="px-4 py-3">
                  <span className="inline-block px-2 py-0.5 rounded-full text-xs bg-[rgba(58,92,47,0.4)] text-[#a8cc8a]">
                    {post.category}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-[#7a9a6a]">{post.author ?? "Unknown"}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleTogglePublish(post)}
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold transition-colors ${
                      post.published_at
                        ? "bg-[rgba(22,163,74,0.15)] text-[#4ade80] hover:bg-[rgba(22,163,74,0.25)]"
                        : "bg-[rgba(255,255,255,0.05)] text-[#5a7050] hover:bg-[rgba(255,255,255,0.1)]"
                    }`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${post.published_at ? "bg-[#4ade80]" : "bg-[#5a7050]"}`}
                    />
                    {post.published_at ? "Published" : "Draft"}
                  </button>
                </td>
                <td className="px-4 py-3 text-center">
                  {post.is_featured ? (
                    <span className="text-yellow-400">⭐</span>
                  ) : (
                    <span className="text-[#3a5030]">—</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/admin/blog/${post.id}`}
                      className="text-xs px-3 py-1.5 rounded-lg border border-[rgba(168,204,138,0.2)] text-[#a8cc8a] hover:bg-[rgba(58,92,47,0.3)] transition-colors"
                    >
                      Edit
                    </Link>
                    <button
                      onClick={() => handleDelete(post.id, post.title)}
                      disabled={deleting === post.id}
                      className="text-xs px-3 py-1.5 rounded-lg text-red-500/60 hover:text-red-400 hover:bg-[rgba(239,68,68,0.1)] transition-colors disabled:opacity-50"
                    >
                      {deleting === post.id ? "…" : "Delete"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {posts.length === 0 && (
          <div className="px-4 py-12 text-center text-[#5a7050]">
            No posts yet.{" "}
            <Link href="/admin/blog/new" className="text-[#a8cc8a] hover:underline">
              Create your first post →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

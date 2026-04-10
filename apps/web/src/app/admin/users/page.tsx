"use client";

import { useEffect, useState } from "react";

import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { adminApi } from "@/lib/adminApi";
import type { AdminUserSummary } from "@/lib/adminTypes";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUserSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadUsers() {
    setLoading(true);
    try {
      const response = await adminApi.listUsers();
      setUsers(response.items);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load users.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadUsers();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Loading members"
          description="Fetching the organization roster and recent account details."
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Users are unavailable"
          description={error}
          variant="error"
          actionLabel="Retry"
          onAction={() => void loadUsers()}
        />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl">
      <div className="mb-8">
        <p className="text-[#5a8050] text-xs font-semibold uppercase tracking-[0.2em] mb-2">
          Admin
        </p>
        <h1 className="font-serif text-3xl text-white">Users</h1>
        <p className="text-[#5a7050] text-sm mt-1">{users.length} members in this organization</p>
      </div>

      <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[rgba(168,204,138,0.08)]">
              {["Email", "Name", "Role", "Status", "Joined", "Last Login"].map((heading) => (
                <th
                  key={heading}
                  className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-[#5a8050]"
                >
                  {heading}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {users.map((user, index) => (
              <tr
                key={user.id}
                className={`border-b border-[rgba(168,204,138,0.06)] ${
                  index % 2 === 0 ? "" : "bg-[rgba(255,255,255,0.01)]"
                }`}
              >
                <td className="px-4 py-3 text-sm text-white">{user.email}</td>
                <td className="px-4 py-3 text-sm text-[#7a9a6a]">
                  {user.fullName || "No name provided"}
                </td>
                <td className="px-4 py-3 text-sm text-[#a8cc8a]">{user.role}</td>
                <td className="px-4 py-3 text-sm">
                  <span
                    className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
                      user.isActive
                        ? "bg-[rgba(22,163,74,0.15)] text-[#4ade80]"
                        : "bg-[rgba(239,68,68,0.12)] text-red-300"
                    }`}
                  >
                    {user.isActive ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-[#7a9a6a]">
                  {new Date(user.createdAt).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-sm text-[#7a9a6a]">
                  {user.lastLoginAt ? new Date(user.lastLoginAt).toLocaleString() : "Never"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {users.length === 0 ? (
          <div className="px-4 py-12 text-center text-[#5a7050]">No users found.</div>
        ) : null}
      </div>
    </div>
  );
}

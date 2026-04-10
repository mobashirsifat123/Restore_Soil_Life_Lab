"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";

import { Button, Input, PageHeader, Panel, Textarea } from "@bio/ui";

import {
  useChangePasswordMutation,
  useProfileQueryWithInitial,
  useRevokeOtherSessionsMutation,
  useRevokeSessionMutation,
  useSessionsQueryWithInitial,
  useUpdateProfileMutation,
} from "../../hooks/use-bio-queries";
import { getApiErrorMessage } from "../../lib/api-errors";
import type { AuthSessionListResponse, MemberProfile } from "@bio/api-client";

type SettingsFormState = {
  fullName: string;
  avatarUrl: string;
  bio: string;
  jobTitle: string;
  location: string;
  phone: string;
  dashboardDensity: string;
  notifyProductUpdates: boolean;
  notifyResearchDigest: boolean;
  notifySecurityAlerts: boolean;
};

const emptyState: SettingsFormState = {
  fullName: "",
  avatarUrl: "",
  bio: "",
  jobTitle: "",
  location: "",
  phone: "",
  dashboardDensity: "comfortable",
  notifyProductUpdates: true,
  notifyResearchDigest: true,
  notifySecurityAlerts: true,
};

function initialsFor(name: string | undefined | null, email: string | undefined | null) {
  const source = (name?.trim() || email?.trim() || "Bio Soil").replace(/\s+/g, " ");
  const parts = source.split(" ").filter(Boolean);
  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase();
  }
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
}

function formatSessionLabel(value: string | null | undefined) {
  if (!value) return "Unavailable";
  return new Date(value).toLocaleString();
}

export function MemberSettings({
  initialProfile,
  initialSessions,
}: {
  initialProfile?: MemberProfile | null;
  initialSessions?: AuthSessionListResponse | null;
}) {
  const router = useRouter();
  const profileQuery = useProfileQueryWithInitial(initialProfile);
  const sessionsQuery = useSessionsQueryWithInitial(initialSessions);
  const [form, setForm] = useState<SettingsFormState>(emptyState);
  const [profileMessage, setProfileMessage] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  useEffect(() => {
    if (!profileQuery.data) return;
    setForm({
      fullName: profileQuery.data.fullName ?? "",
      avatarUrl: profileQuery.data.avatarUrl ?? "",
      bio: profileQuery.data.bio ?? "",
      jobTitle: profileQuery.data.jobTitle ?? "",
      location: profileQuery.data.location ?? "",
      phone: profileQuery.data.phone ?? "",
      dashboardDensity: profileQuery.data.preferences.dashboardDensity ?? "comfortable",
      notifyProductUpdates: profileQuery.data.preferences.notifyProductUpdates,
      notifyResearchDigest: profileQuery.data.preferences.notifyResearchDigest,
      notifySecurityAlerts: profileQuery.data.preferences.notifySecurityAlerts,
    });
  }, [profileQuery.data]);

  const updateProfile = useUpdateProfileMutation({
    onSuccess: () => {
      setProfileError(null);
      setProfileMessage("Your member settings were saved.");
      router.refresh();
    },
    onError: (error) => {
      setProfileMessage(null);
      setProfileError(getApiErrorMessage(error, "Could not save your member settings."));
    },
  });

  const changePassword = useChangePasswordMutation({
    onSuccess: () => {
      setPasswordError(null);
      setPasswordMessage("Password updated successfully.");
      setCurrentPassword("");
      setNewPassword("");
    },
    onError: (error) => {
      setPasswordMessage(null);
      setPasswordError(getApiErrorMessage(error, "Could not update your password."));
    },
  });

  const revokeSession = useRevokeSessionMutation({
    onError: (error) => {
      setPasswordMessage(null);
      setPasswordError(getApiErrorMessage(error, "Could not revoke that session."));
    },
  });

  const revokeOtherSessions = useRevokeOtherSessionsMutation({
    onSuccess: () => {
      setPasswordError(null);
      setPasswordMessage("Other sessions were signed out.");
    },
    onError: (error) => {
      setPasswordMessage(null);
      setPasswordError(getApiErrorMessage(error, "Could not revoke other sessions."));
    },
  });

  const profileDisplayName = useMemo(
    () =>
      form.fullName.trim() || profileQuery.data?.fullName || profileQuery.data?.email || "Member",
    [form.fullName, profileQuery.data],
  );

  function setField<K extends keyof SettingsFormState>(key: K, value: SettingsFormState[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function handleProfileSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setProfileMessage(null);
    setProfileError(null);
    updateProfile.mutate({
      fullName: form.fullName.trim() || null,
      avatarUrl: form.avatarUrl.trim() || null,
      bio: form.bio.trim() || null,
      jobTitle: form.jobTitle.trim() || null,
      location: form.location.trim() || null,
      phone: form.phone.trim() || null,
      dashboardDensity: form.dashboardDensity,
      notifyProductUpdates: form.notifyProductUpdates,
      notifyResearchDigest: form.notifyResearchDigest,
      notifySecurityAlerts: form.notifySecurityAlerts,
    });
  }

  function handlePasswordSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPasswordError(null);
    setPasswordMessage(null);
    changePassword.mutate({
      currentPassword,
      newPassword,
    });
  }

  if (profileQuery.isLoading) {
    return <Panel className="p-8 text-[#5d624e]">Loading your member settings...</Panel>;
  }

  if (profileQuery.isError || !profileQuery.data) {
    return (
      <Panel className="space-y-3 p-8">
        <p className="editorial-kicker font-mono text-xs">Member Settings</p>
        <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
          Sign in to manage your account
        </h2>
        <p className="text-sm leading-7 text-[#5d624e]">
          Profile settings, password changes, and session controls are available once you are signed
          in.
        </p>
      </Panel>
    );
  }

  const sessions = sessionsQuery.data?.items ?? [];
  const currentSession = sessions.find((session) => session.isCurrent) ?? null;

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Member Settings" title="Account and portal preferences">
        Update your profile, change your password, manage active sessions, and tailor the member
        workspace to how you like to work.
      </PageHeader>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Panel className="space-y-6 p-8">
          <div className="flex items-center gap-5">
            {form.avatarUrl.trim() ? (
              <Image
                src={form.avatarUrl}
                alt={profileDisplayName}
                width={80}
                height={80}
                unoptimized
                className="h-20 w-20 rounded-full object-cover ring-4 ring-[rgba(58,92,47,0.12)]"
              />
            ) : (
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-[#1e3318] text-2xl font-semibold text-white ring-4 ring-[rgba(58,92,47,0.12)]">
                {initialsFor(profileDisplayName, profileQuery.data.email)}
              </div>
            )}
            <div>
              <p className="editorial-kicker font-mono text-xs">Member identity</p>
              <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
                {profileDisplayName}
              </h2>
              <p className="mt-1 text-sm text-[#5d624e]">{profileQuery.data.email}</p>
              <p className="text-xs text-[#7c7a67]">
                {profileQuery.data.organizationName ?? "Bio Soil Workspace"}
              </p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl bg-[rgba(58,92,47,0.06)] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#5a7050]">
                Role
              </p>
              <p className="mt-2 text-sm font-semibold text-[#283422]">
                {profileQuery.data.roles.join(", ")}
              </p>
            </div>
            <div className="rounded-2xl bg-[rgba(58,92,47,0.06)] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#5a7050]">
                Current session
              </p>
              <p className="mt-2 text-sm font-semibold text-[#283422]">
                {currentSession ? "Active on this device" : "Checking..."}
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-[rgba(58,92,47,0.12)] bg-[#f8f5ef] p-5">
            <p className="editorial-kicker font-mono text-xs">
              Feature ideas adapted from strong member portals
            </p>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-[#5d624e]">
              <li>1. A clear profile center with editable identity details and photo.</li>
              <li>2. A security area for password and active session management.</li>
              <li>3. Personal workspace preferences that change how the portal feels.</li>
              <li>
                4. Future-ready hooks for alerts, research digests, and personalized onboarding.
              </li>
            </ul>
          </div>
        </Panel>

        <form className="space-y-6" onSubmit={handleProfileSubmit}>
          <Panel className="space-y-6 p-8">
            <div>
              <p className="editorial-kicker font-mono text-xs">Profile</p>
              <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
                Public-facing member details
              </h2>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm font-semibold text-[#283422]">Full name</span>
                <Input
                  value={form.fullName}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    setField("fullName", event.target.value)
                  }
                  placeholder="Mobashir Hossain"
                />
              </label>

              <label className="space-y-2">
                <span className="text-sm font-semibold text-[#283422]">Job title</span>
                <Input
                  value={form.jobTitle}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    setField("jobTitle", event.target.value)
                  }
                  placeholder="Research lead"
                />
              </label>

              <label className="space-y-2">
                <span className="text-sm font-semibold text-[#283422]">Location</span>
                <Input
                  value={form.location}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    setField("location", event.target.value)
                  }
                  placeholder="Dhaka, Bangladesh"
                />
              </label>

              <label className="space-y-2">
                <span className="text-sm font-semibold text-[#283422]">Phone</span>
                <Input
                  value={form.phone}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    setField("phone", event.target.value)
                  }
                  placeholder="+880..."
                />
              </label>
            </div>

            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Profile photo URL</span>
              <Input
                value={form.avatarUrl}
                onChange={(event: ChangeEvent<HTMLInputElement>) =>
                  setField("avatarUrl", event.target.value)
                }
                placeholder="https://..."
              />
              <p className="text-xs leading-6 text-[#7c7a67]">
                Use a direct image URL for now. We can add uploads next if you want.
              </p>
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Short bio</span>
              <Textarea
                value={form.bio}
                onChange={(event: ChangeEvent<HTMLTextAreaElement>) =>
                  setField("bio", event.target.value)
                }
                placeholder="Tell members and researchers what kind of soil work you focus on."
              />
            </label>
          </Panel>

          <Panel className="space-y-6 p-8">
            <div>
              <p className="editorial-kicker font-mono text-xs">Preferences</p>
              <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
                Member workspace behavior
              </h2>
            </div>

            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Dashboard density</span>
              <select
                value={form.dashboardDensity}
                onChange={(event) => setField("dashboardDensity", event.target.value)}
                className="w-full rounded-xl border border-[rgba(58,92,47,0.18)] bg-white px-4 py-3 text-sm text-[#1e3318] outline-none focus:border-[#3a5c2f]"
              >
                <option value="comfortable">Comfortable</option>
                <option value="compact">Compact</option>
                <option value="focused">Focused</option>
              </select>
            </label>

            <div className="space-y-4">
              {[
                [
                  "notifyProductUpdates",
                  "Product updates",
                  "Get notified when SilkSoil and the member portal gain new capabilities.",
                ],
                [
                  "notifyResearchDigest",
                  "Research digest",
                  "Receive curated soil biology insights and member-only research notes.",
                ],
                [
                  "notifySecurityAlerts",
                  "Security alerts",
                  "Always recommended. Receive alerts for password and session changes.",
                ],
              ].map(([key, label, help]) => (
                <label
                  key={key}
                  className="flex items-start gap-3 rounded-2xl border border-[rgba(58,92,47,0.12)] bg-[rgba(255,255,255,0.6)] p-4"
                >
                  <input
                    type="checkbox"
                    className="mt-1 h-4 w-4 rounded border-[rgba(58,92,47,0.25)] text-[#3a5c2f]"
                    checked={form[key as keyof SettingsFormState] as boolean}
                    onChange={(event) =>
                      setField(key as keyof SettingsFormState, event.target.checked as never)
                    }
                  />
                  <div>
                    <p className="text-sm font-semibold text-[#283422]">{label}</p>
                    <p className="text-xs leading-6 text-[#7c7a67]">{help}</p>
                  </div>
                </label>
              ))}
            </div>

            {profileError ? <p className="text-sm text-red-700">{profileError}</p> : null}
            {profileMessage ? <p className="text-sm text-[#2f7d46]">{profileMessage}</p> : null}

            <div className="flex justify-end">
              <Button disabled={updateProfile.isPending} type="submit">
                {updateProfile.isPending ? "Saving..." : "Save account settings"}
              </Button>
            </div>
          </Panel>
        </form>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel className="space-y-6 p-8">
          <div>
            <p className="editorial-kicker font-mono text-xs">Security</p>
            <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
              Change your password
            </h2>
          </div>

          <form className="space-y-5" onSubmit={handlePasswordSubmit}>
            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">Current password</span>
              <Input
                type="password"
                value={currentPassword}
                onChange={(event: ChangeEvent<HTMLInputElement>) =>
                  setCurrentPassword(event.target.value)
                }
                placeholder="Your current password"
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-semibold text-[#283422]">New password</span>
              <Input
                type="password"
                value={newPassword}
                onChange={(event: ChangeEvent<HTMLInputElement>) =>
                  setNewPassword(event.target.value)
                }
                placeholder="A stronger new password"
              />
            </label>

            {passwordError ? <p className="text-sm text-red-700">{passwordError}</p> : null}
            {passwordMessage ? <p className="text-sm text-[#2f7d46]">{passwordMessage}</p> : null}

            <Button
              disabled={
                changePassword.isPending ||
                currentPassword.trim().length < 8 ||
                newPassword.trim().length < 8
              }
              type="submit"
            >
              {changePassword.isPending ? "Updating..." : "Change password"}
            </Button>
          </form>
        </Panel>

        <Panel className="space-y-6 p-8">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="editorial-kicker font-mono text-xs">Sessions</p>
              <h2 className="font-serif text-3xl tracking-[-0.03em] text-[#283422]">
                Devices and active logins
              </h2>
            </div>
            <Button
              disabled={revokeOtherSessions.isPending}
              onClick={() => revokeOtherSessions.mutate()}
              type="button"
              variant="secondary"
            >
              {revokeOtherSessions.isPending ? "Signing out..." : "Sign out other sessions"}
            </Button>
          </div>

          {sessionsQuery.isLoading ? (
            <p className="text-sm text-[#5d624e]">Loading active sessions...</p>
          ) : sessions.length ? (
            <div className="space-y-4">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className="flex flex-wrap items-start justify-between gap-4 rounded-2xl border border-[rgba(58,92,47,0.12)] bg-[rgba(255,255,255,0.65)] p-5"
                >
                  <div className="space-y-1">
                    <p className="text-sm font-semibold text-[#283422]">
                      {session.isCurrent ? "Current device" : "Another active device"}
                    </p>
                    <p className="text-xs leading-5 text-[#7c7a67]">
                      {session.userAgent || "Unknown browser"}
                    </p>
                    <p className="text-xs leading-5 text-[#7c7a67]">
                      Last used: {formatSessionLabel(session.lastUsedAt)}
                    </p>
                    <p className="text-xs leading-5 text-[#7c7a67]">
                      Expires: {formatSessionLabel(session.expiresAt)}
                    </p>
                  </div>

                  {session.isCurrent ? (
                    <span className="rounded-full bg-[#f0f7ed] px-3 py-2 text-xs font-semibold text-[#35542c]">
                      Current session
                    </span>
                  ) : (
                    <Button
                      disabled={revokeSession.isPending}
                      onClick={() => revokeSession.mutate(session.id)}
                      type="button"
                      variant="ghost"
                    >
                      Revoke
                    </Button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm leading-7 text-[#5d624e]">
              Only this device is currently signed in.
            </p>
          )}
        </Panel>
      </div>
    </div>
  );
}

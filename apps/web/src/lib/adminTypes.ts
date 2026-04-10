export interface AdminUserSummary {
  id: string;
  organizationId: string;
  email: string;
  fullName?: string | null;
  role: string;
  isActive: boolean;
  createdAt: string;
  lastLoginAt?: string | null;
}

export interface AdminUserListResponse {
  items: AdminUserSummary[];
}

export interface UserActivityLogEntry {
  happenedAt: string;
  activityType: string;
  activityLabel: string;
  userId?: string | null;
  userEmail?: string | null;
  details?: string | null;
}

export interface UserActivityLogListResponse {
  items: UserActivityLogEntry[];
}

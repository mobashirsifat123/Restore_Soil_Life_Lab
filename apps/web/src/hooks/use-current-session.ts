"use client";

import { ApiError } from "@bio/api-client";
import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../lib/api";
import type { SessionResponse } from "@bio/api-client";

export function useCurrentSession(initialData?: SessionResponse | null) {
  return useQuery({
    queryKey: ["session"],
    queryFn: async () => {
      try {
        return await apiClient.getSession();
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          return null;
        }
        throw error;
      }
    },
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status === 401) {
        return false;
      }
      return failureCount < 2;
    },
    retryDelay: 500,
    refetchOnMount: "always",
    refetchOnWindowFocus: true,
    staleTime: 60_000,
    initialData,
  });
}

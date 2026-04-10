"use client";

import type {
  AuthSessionListResponse,
  ChangePasswordInput,
  MemberProfile,
  ProjectCreate,
  RunCreate,
  RunStatus,
  ScenarioCreate,
  SoilSampleCreate,
  UpdateMemberProfile,
} from "@bio/api-client";
import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationOptions,
  type UseQueryOptions,
} from "@tanstack/react-query";

import { apiClient } from "../lib/api";

const runTerminalStatuses = new Set<RunStatus>(["succeeded", "failed", "canceled"]);

export const bioQueryKeys = {
  projects: ["projects"] as const,
  profile: ["profile"] as const,
  sessions: ["auth-sessions"] as const,
  project: (projectId: string) => ["project", projectId] as const,
  soilSamples: (projectId: string) => ["soil-samples", projectId] as const,
  scenarios: (projectId: string) => ["scenarios", projectId] as const,
  run: (runId: string) => ["run", runId] as const,
  runStatus: (runId: string) => ["run-status", runId] as const,
  runResults: (runId: string) => ["run-results", runId] as const,
};

export function useProjectsQuery() {
  return useQuery({
    queryKey: bioQueryKeys.projects,
    queryFn: () => apiClient.listProjects(),
  });
}

export function useProfileQuery() {
  return useQuery({
    queryKey: bioQueryKeys.profile,
    queryFn: () => apiClient.getProfile(),
  });
}

export function useProfileQueryWithInitial(initialData?: MemberProfile | null) {
  return useQuery({
    queryKey: bioQueryKeys.profile,
    queryFn: () => apiClient.getProfile(),
    initialData: initialData ?? undefined,
  });
}

export function useSessionsQuery() {
  return useQuery({
    queryKey: bioQueryKeys.sessions,
    queryFn: () => apiClient.listSessions(),
  });
}

export function useSessionsQueryWithInitial(initialData?: AuthSessionListResponse | null) {
  return useQuery({
    queryKey: bioQueryKeys.sessions,
    queryFn: () => apiClient.listSessions(),
    initialData: initialData ?? undefined,
  });
}

export function useProjectQuery(projectId: string) {
  return useQuery({
    queryKey: bioQueryKeys.project(projectId),
    queryFn: () => apiClient.getProject(projectId),
  });
}

export function useSoilSamplesQuery(projectId: string) {
  return useQuery({
    queryKey: bioQueryKeys.soilSamples(projectId),
    queryFn: () => apiClient.listSoilSamples(projectId),
  });
}

export function useScenariosQuery(projectId: string) {
  return useQuery({
    queryKey: bioQueryKeys.scenarios(projectId),
    queryFn: () => apiClient.listScenarios(projectId),
  });
}

type CreateProjectOptions = Omit<
  UseMutationOptions<Awaited<ReturnType<typeof apiClient.createProject>>, Error, ProjectCreate>,
  "mutationFn"
>;

export function useCreateProjectMutation(options?: CreateProjectOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ProjectCreate) => apiClient.createProject(payload),
    ...options,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.projects });
      await options?.onSuccess?.(data, variables, onMutateResult, context);
    },
  });
}

type UpdateProfileOptions = Omit<
  UseMutationOptions<MemberProfile, Error, UpdateMemberProfile>,
  "mutationFn"
>;

export function useUpdateProfileMutation(options?: UpdateProfileOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: UpdateMemberProfile) => apiClient.updateProfile(payload),
    ...options,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.profile });
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.sessions });
      await options?.onSuccess?.(data, variables, onMutateResult, context);
    },
  });
}

type ChangePasswordOptions = Omit<
  UseMutationOptions<void, Error, ChangePasswordInput>,
  "mutationFn"
>;

export function useChangePasswordMutation(options?: ChangePasswordOptions) {
  return useMutation({
    mutationFn: (payload: ChangePasswordInput) => apiClient.changePassword(payload),
    ...options,
  });
}

type RevokeSessionOptions = Omit<UseMutationOptions<void, Error, string>, "mutationFn">;

export function useRevokeSessionMutation(options?: RevokeSessionOptions) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => apiClient.revokeSession(sessionId),
    ...options,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.sessions });
      await options?.onSuccess?.(data, variables, onMutateResult, context);
    },
  });
}

type RevokeOtherSessionsOptions = Omit<UseMutationOptions<void, Error, void>, "mutationFn">;

export function useRevokeOtherSessionsMutation(options?: RevokeOtherSessionsOptions) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.revokeOtherSessions(),
    ...options,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.sessions });
      await options?.onSuccess?.(data, variables, onMutateResult, context);
    },
  });
}

type CreateSoilSampleOptions = Omit<
  UseMutationOptions<
    Awaited<ReturnType<typeof apiClient.createSoilSample>>,
    Error,
    SoilSampleCreate
  >,
  "mutationFn"
>;

export function useCreateSoilSampleMutation(projectId: string, options?: CreateSoilSampleOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SoilSampleCreate) => apiClient.createSoilSample(projectId, payload),
    ...options,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.soilSamples(projectId) });
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.project(projectId) });
      await options?.onSuccess?.(data, variables, onMutateResult, context);
    },
  });
}

type CreateScenarioOptions = Omit<
  UseMutationOptions<Awaited<ReturnType<typeof apiClient.createScenario>>, Error, ScenarioCreate>,
  "mutationFn"
>;

export function useCreateScenarioMutation(projectId: string, options?: CreateScenarioOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ScenarioCreate) => apiClient.createScenario(projectId, payload),
    ...options,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.scenarios(projectId) });
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.project(projectId) });
      await options?.onSuccess?.(data, variables, onMutateResult, context);
    },
  });
}

type CreateRunOptions = Omit<
  UseMutationOptions<Awaited<ReturnType<typeof apiClient.createRun>>, Error, RunCreate>,
  "mutationFn"
>;

export function useCreateRunMutation(projectId: string, options?: CreateRunOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: RunCreate) => apiClient.createRun(payload),
    ...options,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.project(projectId) });
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.run(data.id) });
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.runStatus(data.id) });
      await queryClient.invalidateQueries({ queryKey: bioQueryKeys.runResults(data.id) });
      await options?.onSuccess?.(data, variables, onMutateResult, context);
    },
  });
}

export function useRunsQuery() {
  return useQuery({
    queryKey: ["runs"],
    queryFn: () => apiClient.listRuns(),
  });
}

export function useRunQuery(runId: string) {
  return useQuery({
    queryKey: bioQueryKeys.run(runId),
    queryFn: () => apiClient.getRun(runId),
  });
}

type RunStatusQueryOptions = Omit<
  UseQueryOptions<
    Awaited<ReturnType<typeof apiClient.getRunStatus>>,
    Error,
    Awaited<ReturnType<typeof apiClient.getRunStatus>>,
    ReturnType<typeof bioQueryKeys.runStatus>
  >,
  "queryKey" | "queryFn"
>;

export function useRunStatusQuery(runId: string, options?: RunStatusQueryOptions) {
  return useQuery({
    queryKey: bioQueryKeys.runStatus(runId),
    queryFn: () => apiClient.getRunStatus(runId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status && runTerminalStatuses.has(status) ? false : 2_000;
    },
    ...options,
  });
}

export function useRunResultsQuery(runId: string, enabled = true) {
  return useQuery({
    queryKey: bioQueryKeys.runResults(runId),
    queryFn: () => apiClient.getRunResults(runId),
    enabled,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status && runTerminalStatuses.has(status) ? false : 2_000;
    },
  });
}

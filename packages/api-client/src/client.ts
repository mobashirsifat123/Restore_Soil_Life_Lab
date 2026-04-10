import type {
  AuthSessionListResponse,
  ChatAdminConfig,
  ChatAttachment,
  ChatAssistant,
  ChatAssistantUpsert,
  ChatConversationCreate,
  ChatConversationDetail,
  ChatConversationListResponse,
  ChatKnowledgeSource,
  ChatKnowledgeSourceCreate,
  ChatMessage,
  ChatMessageCreate,
  ChatReindexResponse,
  ChatSoilAnalysisInput,
  ChatSoilAnalysisResponse,
  ChatWidgetConfig,
  ChatWidgetConfigUpdate,
  ChangePasswordInput,
  MemberProfile,
  ProjectCreate,
  ProjectDetail,
  ProjectListResponse,
  RunCreate,
  RunDetail,
  RunListResponse,
  RunResultsResponse,
  RunStatusResponse,
  ScenarioCreate,
  ScenarioDetail,
  ScenarioListResponse,
  SessionResponse,
  SoilSampleCreate,
  SoilSampleDetail,
  SoilSampleListResponse,
  UpdateMemberProfile,
} from "./types";

export interface ApiClientOptions {
  baseUrl: string;
  fetcher?: typeof fetch;
  headers?: HeadersInit;
}

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export class BioApiClient {
  private readonly baseUrl: string;
  private readonly fetcher: typeof fetch;
  private readonly headers: HeadersInit;

  constructor(options: ApiClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, "");
    const baseFetcher = options.fetcher ?? fetch;
    this.fetcher = ((input: RequestInfo | URL, init?: RequestInit) =>
      baseFetcher.call(globalThis, input, init)) as typeof fetch;
    this.headers = options.headers ?? {};
  }

  async getSession(): Promise<SessionResponse> {
    return this.request<SessionResponse>("/auth/session");
  }

  async getProfile(): Promise<MemberProfile> {
    return this.request<MemberProfile>("/auth/profile");
  }

  async updateProfile(payload: UpdateMemberProfile): Promise<MemberProfile> {
    return this.request<MemberProfile>("/auth/profile", {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  }

  async changePassword(payload: ChangePasswordInput): Promise<void> {
    await this.requestNoContent("/auth/change-password", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async listSessions(): Promise<AuthSessionListResponse> {
    return this.request<AuthSessionListResponse>("/auth/sessions");
  }

  async revokeSession(sessionId: string): Promise<void> {
    await this.requestNoContent(`/auth/sessions/${sessionId}`, {
      method: "DELETE",
    });
  }

  async revokeOtherSessions(): Promise<void> {
    await this.requestNoContent("/auth/sessions/revoke-others", {
      method: "POST",
    });
  }

  async getChatWidgetConfig(guestToken?: string): Promise<ChatWidgetConfig> {
    return this.request<ChatWidgetConfig>("/chat/widget-config", {
      headers: this.chatHeaders(guestToken),
    });
  }

  async listChatConversations(guestToken?: string): Promise<ChatConversationListResponse> {
    return this.request<ChatConversationListResponse>("/chat/conversations", {
      headers: this.chatHeaders(guestToken),
    });
  }

  async createChatConversation(
    payload: ChatConversationCreate,
    guestToken?: string,
  ): Promise<ChatConversationDetail> {
    return this.request<ChatConversationDetail>("/chat/conversations", {
      method: "POST",
      body: JSON.stringify(payload),
      headers: this.chatHeaders(guestToken),
    });
  }

  async getChatConversation(
    conversationId: string,
    guestToken?: string,
  ): Promise<ChatConversationDetail> {
    return this.request<ChatConversationDetail>(`/chat/conversations/${conversationId}`, {
      headers: this.chatHeaders(guestToken),
    });
  }

  async sendChatMessage(
    conversationId: string,
    payload: ChatMessageCreate,
    guestToken?: string,
  ): Promise<ChatMessage> {
    return this.request<ChatMessage>(`/chat/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify(payload),
      headers: this.chatHeaders(guestToken),
    });
  }

  async uploadChatAttachment(conversationId: string, file: File, guestToken?: string) {
    const form = new FormData();
    form.append("file", file);
    return this.request<ChatAttachment>(`/chat/conversations/${conversationId}/attachments`, {
      method: "POST",
      body: form,
      headers: this.chatHeaders(guestToken),
    });
  }

  async runChatSoilAnalysis(
    payload: ChatSoilAnalysisInput,
    guestToken?: string,
  ): Promise<ChatSoilAnalysisResponse> {
    return this.request<ChatSoilAnalysisResponse>("/chat/tools/soil-analysis", {
      method: "POST",
      body: JSON.stringify(payload),
      headers: this.chatHeaders(guestToken),
    });
  }

  async getAdminChatConfig(): Promise<ChatAdminConfig> {
    return this.request<ChatAdminConfig>("/admin/chat/config");
  }

  async updateAdminChatConfig(payload: ChatWidgetConfigUpdate): Promise<ChatWidgetConfig> {
    return this.request<ChatWidgetConfig>("/admin/chat/config", {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  }

  async listAdminChatAssistants(): Promise<ChatAssistant[]> {
    return this.request<ChatAssistant[]>("/admin/chat/assistants");
  }

  async createAdminChatAssistant(payload: ChatAssistantUpsert): Promise<ChatAssistant> {
    return this.request<ChatAssistant>("/admin/chat/assistants", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async updateAdminChatAssistant(
    assistantId: string,
    payload: ChatAssistantUpsert,
  ): Promise<ChatAssistant> {
    return this.request<ChatAssistant>(`/admin/chat/assistants/${assistantId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  }

  async listAdminChatSources(): Promise<ChatKnowledgeSource[]> {
    const response = await this.request<{ items: ChatKnowledgeSource[] }>("/admin/chat/sources");
    return response.items;
  }

  async createAdminChatSource(payload: ChatKnowledgeSourceCreate): Promise<ChatKnowledgeSource> {
    return this.request<ChatKnowledgeSource>("/admin/chat/sources", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async reindexAdminChatSource(sourceId: string): Promise<ChatReindexResponse> {
    return this.request<ChatReindexResponse>(`/admin/chat/sources/${sourceId}/reindex`, {
      method: "POST",
    });
  }

  async listProjects(): Promise<ProjectListResponse> {
    return this.request<ProjectListResponse>("/projects");
  }

  async createProject(payload: ProjectCreate): Promise<ProjectDetail> {
    return this.request<ProjectDetail>("/projects", {
      body: JSON.stringify(payload),
      method: "POST",
    });
  }

  async getProject(projectId: string): Promise<ProjectDetail> {
    return this.request<ProjectDetail>(`/projects/${projectId}`);
  }

  async listSoilSamples(projectId: string): Promise<SoilSampleListResponse> {
    return this.request<SoilSampleListResponse>(`/projects/${projectId}/soil-samples`);
  }

  async createSoilSample(projectId: string, payload: SoilSampleCreate): Promise<SoilSampleDetail> {
    return this.request<SoilSampleDetail>(`/projects/${projectId}/soil-samples`, {
      body: JSON.stringify(payload),
      method: "POST",
    });
  }

  async listScenarios(projectId: string): Promise<ScenarioListResponse> {
    return this.request<ScenarioListResponse>(`/projects/${projectId}/scenarios`);
  }

  async createScenario(projectId: string, payload: ScenarioCreate): Promise<ScenarioDetail> {
    return this.request<ScenarioDetail>(`/projects/${projectId}/scenarios`, {
      body: JSON.stringify(payload),
      method: "POST",
    });
  }

  async createRun(payload: RunCreate): Promise<RunDetail> {
    return this.request<RunDetail>("/runs", {
      body: JSON.stringify(payload),
      method: "POST",
    });
  }

  async listRuns(): Promise<RunListResponse> {
    return this.request<RunListResponse>("/runs");
  }

  async getRun(runId: string): Promise<RunDetail> {
    return this.request<RunDetail>(`/runs/${runId}`);
  }

  async getRunStatus(runId: string): Promise<RunStatusResponse> {
    return this.request<RunStatusResponse>(`/runs/${runId}/status`);
  }

  async getRunResults(runId: string): Promise<RunResultsResponse> {
    return this.request<RunResultsResponse>(`/runs/${runId}/results`);
  }

  private chatHeaders(guestToken?: string): HeadersInit {
    return guestToken ? { "X-Bio-Guest-Id": guestToken } : {};
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
    const response = await this.fetcher(`${this.baseUrl}${path}`, {
      ...init,
      credentials: "include",
      headers: {
        ...this.headers,
        ...(isFormData ? {} : { "content-type": "application/json" }),
        ...(init?.headers ?? {}),
      },
    });

    if (!response.ok) {
      let body: unknown = null;
      try {
        body = await response.json();
      } catch {
        body = await response.text();
      }
      throw new ApiError(`Request failed with status ${response.status}`, response.status, body);
    }

    return (await response.json()) as T;
  }

  private async requestNoContent(path: string, init?: RequestInit): Promise<void> {
    const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
    const response = await this.fetcher(`${this.baseUrl}${path}`, {
      ...init,
      credentials: "include",
      headers: {
        ...this.headers,
        ...(isFormData ? {} : { "content-type": "application/json" }),
        ...(init?.headers ?? {}),
      },
    });

    if (!response.ok) {
      let body: unknown = null;
      try {
        body = await response.json();
      } catch {
        body = await response.text();
      }
      throw new ApiError(`Request failed with status ${response.status}`, response.status, body);
    }
  }
}

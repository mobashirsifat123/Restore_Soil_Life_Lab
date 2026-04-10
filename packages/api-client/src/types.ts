export type JsonValue =
  | string
  | number
  | boolean
  | null
  | { [key: string]: JsonValue }
  | JsonValue[];

export type JsonObject = { [key: string]: JsonValue };

export type ProjectStatus = "active" | "archived";
export type ScenarioStatus = "active" | "archived";
export type RunStatus =
  | "draft"
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "cancel_requested"
  | "canceled";
export type ArtifactType =
  | "result_json"
  | "summary_json"
  | "csv_export"
  | "plot_image"
  | "report_pdf"
  | "log_bundle"
  | "other";

export interface SessionUser {
  id: string;
  email: string;
  fullName?: string | null;
  roles: string[];
  permissions: string[];
}

export interface SessionResponse {
  user: SessionUser;
  activeOrganizationId: string;
}

export interface MemberPreferences {
  dashboardDensity: string;
  notifyProductUpdates: boolean;
  notifyResearchDigest: boolean;
  notifySecurityAlerts: boolean;
}

export interface MemberProfile {
  id: string;
  email: string;
  fullName?: string | null;
  avatarUrl?: string | null;
  bio?: string | null;
  jobTitle?: string | null;
  location?: string | null;
  phone?: string | null;
  organizationName?: string | null;
  roles: string[];
  preferences: MemberPreferences;
  createdAt: string;
  updatedAt: string;
}

export interface UpdateMemberProfile {
  fullName?: string | null;
  avatarUrl?: string | null;
  bio?: string | null;
  jobTitle?: string | null;
  location?: string | null;
  phone?: string | null;
  dashboardDensity?: string | null;
  notifyProductUpdates?: boolean | null;
  notifyResearchDigest?: boolean | null;
  notifySecurityAlerts?: boolean | null;
}

export interface ChangePasswordInput {
  currentPassword: string;
  newPassword: string;
}

export interface AuthSessionSummary {
  id: string;
  userAgent?: string | null;
  ipAddress?: string | null;
  createdAt: string;
  lastUsedAt?: string | null;
  expiresAt: string;
  isCurrent: boolean;
}

export interface AuthSessionListResponse {
  items: AuthSessionSummary[];
}

export interface ChatCitation {
  title: string;
  sourceType: string;
  snippet?: string | null;
  sourceUrl?: string | null;
}

export interface ChatAttachment {
  id: string;
  attachmentType: string;
  filename: string;
  mimeType?: string | null;
  byteSize?: number | null;
  createdAt: string;
}

export interface ChatMessage {
  id: string;
  role: string;
  content: string;
  structuredPayload: JsonObject;
  citations: ChatCitation[];
  metadata: JsonObject;
  latencyMs?: number | null;
  createdAt: string;
}

export interface ChatConversationSummary {
  id: string;
  title?: string | null;
  channel: string;
  status: string;
  summary?: string | null;
  lastActivityAt: string;
  createdAt: string;
}

export interface ChatConversationDetail extends ChatConversationSummary {
  messages: ChatMessage[];
  attachments: ChatAttachment[];
}

export interface ChatConversationListResponse {
  items: ChatConversationSummary[];
}

export interface ChatConversationCreate {
  title?: string | null;
  channel?: string | null;
}

export interface ChatMessageCreate {
  content: string;
  toolHint?: string | null;
  quickAction?: string | null;
  attachmentIds?: string[];
  metadata?: JsonObject;
}

export interface ChatWidgetGreeting {
  guestTitle: string;
  guestBody: string;
  memberTitle: string;
  memberBody: string;
}

export interface ChatWidgetConfig {
  id: string;
  heroCtaLabel: string;
  heroSubtitle: string;
  launcherLabel: string;
  guestTeaserLimit: number;
  greeting: ChatWidgetGreeting;
  quickActions: JsonObject[];
  theme: JsonObject;
}

export interface ChatSoilAnalysisInput {
  ph: number;
  organicMatter: number;
  moisture: number;
  temperature: number;
  bacteria: number;
  fungi: number;
  protozoa?: number;
  nematodes?: number;
  compaction?: number | null;
  nitrateN?: number | null;
  soilTexture?: string | null;
  productionSystem?: string | null;
}

export interface ChatSoilAnalysisResponse {
  score: number;
  band: string;
  summary: string;
  formulaName?: string | null;
  recommendations: string[];
  componentScores: JsonObject;
  citations: ChatCitation[];
}

export interface ChatAssistantPromptPack {
  generalPrompt: string;
  soilPrompt: string;
  pestPrompt: string;
  marketPrompt: string;
  weatherPrompt: string;
  memberPrompt: string;
  fallbackRules: JsonObject;
  refusalRules: JsonObject;
}

export interface ChatAssistant {
  id: string;
  slug: string;
  name: string;
  provider: string;
  model: string;
  accessMode: string;
  enabledTools: string[];
  supportedLanguages: string[];
  config: JsonObject;
  isActive: boolean;
  promptPack: ChatAssistantPromptPack;
  createdAt: string;
  updatedAt: string;
}

export interface ChatAssistantUpsert {
  slug: string;
  name: string;
  provider: string;
  model: string;
  accessMode: string;
  enabledTools: string[];
  supportedLanguages: string[];
  config: JsonObject;
  isActive: boolean;
  promptPack: ChatAssistantPromptPack;
}

export interface ChatKnowledgeSource {
  id: string;
  sourceType: string;
  title: string;
  bodyText?: string | null;
  sourceUrl?: string | null;
  isEnabled: boolean;
  metadata: JsonObject;
  reindexedAt?: string | null;
  createdAt: string;
}

export interface ChatKnowledgeSourceCreate {
  sourceType: string;
  title: string;
  bodyText?: string | null;
  sourceUrl?: string | null;
  isEnabled?: boolean;
  metadata?: JsonObject;
}

export interface ChatKnowledgeSourceListResponse {
  items: ChatKnowledgeSource[];
}

export interface ChatAnalytics {
  conversationCount: number;
  messageCount: number;
  lowConfidenceCount: number;
  failedToolRuns: number;
}

export interface ChatAdminConfig {
  widget: ChatWidgetConfig;
  activeAssistant?: ChatAssistant | null;
  analytics: ChatAnalytics;
}

export interface ChatWidgetConfigUpdate {
  heroCtaLabel?: string | null;
  heroSubtitle?: string | null;
  launcherLabel?: string | null;
  guestTeaserLimit?: number | null;
  greeting?: ChatWidgetGreeting | null;
  quickActions?: JsonObject[] | null;
  theme?: JsonObject | null;
}

export interface ChatReindexResponse {
  sourceId: string;
  chunkCount: number;
  reindexedAt: string;
}

export interface ProjectCreate {
  name: string;
  slug?: string | null;
  description?: string | null;
  metadata?: JsonObject;
}

export interface ProjectDetail {
  id: string;
  organizationId: string;
  name: string;
  slug: string;
  description?: string | null;
  status: ProjectStatus;
  metadata: JsonObject;
  createdAt: string;
  updatedAt: string;
}

export interface ProjectListResponse {
  items: ProjectDetail[];
  nextCursor?: string | null;
}

export interface SoilSampleCreate {
  sampleCode: string;
  name?: string | null;
  description?: string | null;
  collectedOn?: string | null;
  location?: JsonObject;
  measurements?: JsonObject;
  metadata?: JsonObject;
}

export interface SoilSampleDetail {
  id: string;
  organizationId: string;
  projectId: string;
  sampleCode: string;
  currentVersionId: string;
  currentVersion: number;
  name?: string | null;
  description?: string | null;
  collectedOn?: string | null;
  location: JsonObject;
  measurements: JsonObject;
  metadata: JsonObject;
  createdAt: string;
  updatedAt: string;
}

export interface SoilSampleListResponse {
  items: SoilSampleDetail[];
  nextCursor?: string | null;
}

export interface FoodWebNodeInput {
  key: string;
  label: string;
  trophicGroup: string;
  biomassCarbon: number;
  biomassNitrogen?: number | null;
  isDetritus?: boolean;
  metadata?: JsonObject;
}

export interface FoodWebLinkInput {
  source: string;
  target: string;
  weight?: number;
  metadata?: JsonObject;
}

export interface FoodWebDraft {
  name: string;
  description?: string | null;
  nodes: FoodWebNodeInput[];
  links: FoodWebLinkInput[];
  metadata?: JsonObject;
}

export interface ParameterSetDraft {
  name: string;
  description?: string | null;
  parameters: JsonObject;
  metadata?: JsonObject;
}

export interface ScenarioCreate {
  name: string;
  description?: string | null;
  soilSampleId: string;
  foodWeb: FoodWebDraft;
  parameterSet: ParameterSetDraft;
  scenarioConfig?: JsonObject;
}

export interface ScenarioSoilSampleReference {
  soilSampleId: string;
  soilSampleVersionId?: string | null;
  role?: string | null;
  weight?: number | null;
  metadata?: JsonObject;
}

export interface ScenarioDetail {
  id: string;
  organizationId: string;
  projectId: string;
  stableKey: string;
  version: number;
  name: string;
  description?: string | null;
  status: ScenarioStatus;
  soilSampleId: string;
  soilSampleVersionId: string;
  soilSampleReferences?: ScenarioSoilSampleReference[];
  foodWebDefinitionId: string;
  parameterSetId: string;
  scenarioConfig: JsonObject;
  createdAt: string;
  updatedAt: string;
}

export interface ScenarioListResponse {
  items: ScenarioDetail[];
  nextCursor?: string | null;
}

export interface RunExecutionOptions {
  deterministic?: boolean;
  randomSeed?: number;
  requestedModules?: string[];
  timeoutSeconds?: number;
  metadata?: JsonObject;
}

export interface RunCreate {
  scenarioId: string;
  idempotencyKey?: string | null;
  executionOptions?: RunExecutionOptions;
}

export interface RunDetail {
  id: string;
  organizationId: string;
  projectId: string;
  scenarioId: string;
  status: RunStatus;
  engineName: string;
  engineVersion: string;
  inputSchemaVersion: string;
  parameterSetVersion: number;
  soilSampleVersion: number;
  inputHash: string;
  resultHash?: string | null;
  queuedAt?: string | null;
  startedAt?: string | null;
  completedAt?: string | null;
  canceledAt?: string | null;
  failureCode?: string | null;
  failureMessage?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface RunStatusResponse {
  id: string;
  status: RunStatus;
  queuedAt?: string | null;
  startedAt?: string | null;
  completedAt?: string | null;
  canceledAt?: string | null;
  failureCode?: string | null;
  failureMessage?: string | null;
}

export interface RunArtifact {
  id: string;
  artifactType: ArtifactType;
  label: string;
  contentType: string;
  storageKey: string;
  byteSize?: number | null;
  checksumSha256?: string | null;
  metadata: JsonObject;
  createdAt: string;
}

export interface RunListResponse {
  items: RunDetail[];
  nextCursor?: string;
  hasMore: boolean;
}

export interface RunResultsResponse {
  id: string;
  status: RunStatus;
  engineName: string;
  engineVersion: string;
  parameterSetVersion: number;
  soilSampleVersion: number;
  inputHash: string;
  resultHash?: string | null;
  failureCode?: string | null;
  failureMessage?: string | null;
  inputSnapshot: JsonObject;
  resultSummary?: JsonObject | null;
  artifacts: RunArtifact[];
}

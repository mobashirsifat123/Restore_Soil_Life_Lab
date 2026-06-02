import { createServer } from "node:http";
import { randomUUID } from "node:crypto";

const port = Number.parseInt(process.env.PLAYWRIGHT_TEST_API_PORT ?? "8100", 10);
const webPort = Number.parseInt(process.env.PLAYWRIGHT_TEST_WEB_PORT ?? "3100", 10);
const frontendUrl =
  process.env.PLAYWRIGHT_TEST_BASE_URL ?? `http://127.0.0.1:${webPort}`;
const sessionCookieName = "bio_session";
const nowIso = () => new Date().toISOString();

const state = {
  users: new Map(),
  sessions: new Map(),
  resetTokens: new Map(),
  projects: new Map(),
  projectOrder: [],
  soilSamples: new Map(),
  scenarios: new Map(),
  runs: new Map(),
  runsByProject: new Map(),
};

function json(response, statusCode, body, headers = {}) {
  response.writeHead(statusCode, {
    "content-type": "application/json",
    ...headers,
  });
  response.end(JSON.stringify(body));
}

function noContent(response, headers = {}) {
  response.writeHead(204, headers);
  response.end();
}

function readBody(request) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    request.on("data", (chunk) => chunks.push(chunk));
    request.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf8");
      if (!raw) {
        resolve({});
        return;
      }

      try {
        resolve(JSON.parse(raw));
      } catch (error) {
        reject(error);
      }
    });
    request.on("error", reject);
  });
}

function cookieValue(request, name) {
  const header = request.headers.cookie;
  if (!header) {
    return null;
  }

  for (const pair of header.split(";")) {
    const [key, value] = pair.trim().split("=");
    if (key === name) {
      return value ?? null;
    }
  }

  return null;
}

function authenticatedUser(request) {
  const token = cookieValue(request, sessionCookieName);
  if (!token) {
    return null;
  }

  const userId = state.sessions.get(token);
  if (!userId) {
    return null;
  }

  return state.users.get(userId) ?? null;
}

function sessionPayload(user) {
  return {
    user: {
      id: user.id,
      email: user.email,
      fullName: user.fullName,
      roles: user.roles,
      permissions: user.permissions,
    },
    activeOrganizationId: user.organizationId,
  };
}

function parseUrl(request) {
  return new URL(request.url ?? "/", `http://127.0.0.1:${port}`);
}

function requireAuth(request, response) {
  const user = authenticatedUser(request);
  if (!user) {
    json(response, 401, {
      error: {
        code: "auth_required",
        message: "Authentication is required.",
        details: {},
        issues: [],
      },
    });
    return null;
  }

  return user;
}

function createUser({ email, password, fullName, organizationName }) {
  const userId = randomUUID();
  const organizationId = randomUUID();
  const user = {
    id: userId,
    organizationId,
    email,
    password,
    fullName,
    organizationName,
    roles: ["scientist"],
    permissions: [
      "project:read",
      "project:write",
      "sample:read",
      "sample:write",
      "scenario:read",
      "scenario:write",
      "run:read",
      "run:submit",
    ],
  };
  state.users.set(userId, user);
  return user;
}

function setSession(response, user) {
  const token = randomUUID();
  state.sessions.set(token, user.id);
  return `${sessionCookieName}=${token}; Path=/; HttpOnly; SameSite=Lax`;
}

function clearSession(response, request) {
  const token = cookieValue(request, sessionCookieName);
  if (token) {
    state.sessions.delete(token);
  }
  return `${sessionCookieName}=; Path=/; HttpOnly; Max-Age=0; SameSite=Lax`;
}

function projectSummary(project) {
  return {
    id: project.id,
    organizationId: project.organizationId,
    name: project.name,
    slug: project.slug,
    description: project.description,
    status: "active",
    metadata: project.metadata,
    createdAt: project.createdAt,
    updatedAt: project.updatedAt,
  };
}

function sampleSummary(sample) {
  return {
    id: sample.id,
    organizationId: sample.organizationId,
    projectId: sample.projectId,
    sampleCode: sample.sampleCode,
    currentVersionId: sample.currentVersionId,
    currentVersion: 1,
    name: sample.name,
    description: sample.description,
    collectedOn: sample.collectedOn,
    location: sample.location,
    measurements: sample.measurements,
    metadata: sample.metadata,
    createdAt: sample.createdAt,
    updatedAt: sample.updatedAt,
  };
}

function scenarioSummary(scenario) {
  return {
    id: scenario.id,
    organizationId: scenario.organizationId,
    projectId: scenario.projectId,
    stableKey: scenario.stableKey,
    version: 1,
    name: scenario.name,
    description: scenario.description,
    status: "active",
    soilSampleId: scenario.soilSampleId,
    soilSampleVersionId: scenario.soilSampleVersionId,
    soilSampleReferences: [],
    foodWebDefinitionId: scenario.foodWebDefinitionId,
    parameterSetId: scenario.parameterSetId,
    scenarioConfig: scenario.scenarioConfig,
    createdAt: scenario.createdAt,
    updatedAt: scenario.updatedAt,
  };
}

function runSummary(run) {
  return {
    id: run.id,
    organizationId: run.organizationId,
    projectId: run.projectId,
    scenarioId: run.scenarioId,
    status: run.status,
    engineName: run.engineName,
    engineVersion: run.engineVersion,
    inputSchemaVersion: run.inputSchemaVersion,
    parameterSetVersion: 1,
    soilSampleVersion: 1,
    inputHash: run.inputHash,
    resultHash: run.resultHash,
    queuedAt: run.queuedAt,
    startedAt: run.startedAt,
    completedAt: run.completedAt,
    canceledAt: null,
    failureCode: null,
    failureMessage: null,
    createdAt: run.createdAt,
    updatedAt: run.updatedAt,
  };
}

function runStatus(run) {
  return {
    id: run.id,
    status: run.status,
    queuedAt: run.queuedAt,
    startedAt: run.startedAt,
    completedAt: run.completedAt,
    canceledAt: null,
    failureCode: null,
    failureMessage: null,
  };
}

function runResults(run) {
  return {
    id: run.id,
    status: run.status,
    engineName: run.engineName,
    engineVersion: run.engineVersion,
    parameterSetVersion: 1,
    soilSampleVersion: 1,
    inputHash: run.inputHash,
    resultHash: run.resultHash,
    failureCode: null,
    failureMessage: null,
    inputSnapshot: run.inputSnapshot,
    resultSummary: run.resultSummary,
    artifacts: [
      {
        id: randomUUID(),
        artifactType: "summary_json",
        label: "Result summary",
        contentType: "application/json",
        storageKey: `runs/${run.id}/summary.json`,
        byteSize: 512,
        checksumSha256: null,
        metadata: {},
        createdAt: nowIso(),
      },
    ],
  };
}

const server = createServer(async (request, response) => {
  const url = parseUrl(request);
  const { pathname } = url;

  try {
    if (request.method === "POST" && pathname === "/api/v1/auth/register") {
      const payload = await readBody(request);
      const email = String(payload.email ?? "").trim().toLowerCase();
      if (!email || !payload.password) {
        json(response, 422, {
          error: {
            code: "validation_error",
            message: "Email and password are required.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      const existing = Array.from(state.users.values()).find((user) => user.email === email);
      if (existing) {
        json(response, 409, {
          error: {
            code: "email_already_registered",
            message: "An account with that email already exists.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      const user = createUser({
        email,
        password: String(payload.password),
        fullName: String(payload.name ?? "").trim() || "Bio Soil Member",
        organizationName: payload.organizationName ? String(payload.organizationName) : null,
      });

      json(response, 200, sessionPayload(user), {
        "set-cookie": setSession(response, user),
      });
      return;
    }

    if (request.method === "POST" && pathname === "/api/v1/auth/login") {
      const payload = await readBody(request);
      const email = String(payload.email ?? "").trim().toLowerCase();
      const password = String(payload.password ?? "");
      const user = Array.from(state.users.values()).find((candidate) => candidate.email === email);

      if (!user || user.password !== password) {
        json(response, 401, {
          error: {
            code: "invalid_credentials",
            message: "Invalid email or password.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      json(response, 200, sessionPayload(user), {
        "set-cookie": setSession(response, user),
      });
      return;
    }

    if (request.method === "POST" && pathname === "/api/v1/auth/logout") {
      noContent(response, {
        "set-cookie": clearSession(response, request),
      });
      return;
    }

    if (request.method === "GET" && pathname === "/api/v1/auth/session") {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      json(response, 200, sessionPayload(user));
      return;
    }

    if (request.method === "POST" && pathname === "/api/v1/auth/forgot-password") {
      const payload = await readBody(request);
      const email = String(payload.email ?? "").trim().toLowerCase();
      const user = Array.from(state.users.values()).find((candidate) => candidate.email === email);
      const token = randomUUID();

      if (user) {
        state.resetTokens.set(token, user.id);
      }

      json(response, 200, {
        message: "If that account exists, a password reset link has been sent.",
        developmentResetUrl: `${frontendUrl}/reset-password?token=${token}`,
      });
      return;
    }

    if (request.method === "POST" && pathname === "/api/v1/auth/reset-password") {
      const payload = await readBody(request);
      const token = String(payload.token ?? "");
      const newPassword = String(payload.newPassword ?? "");
      const userId = state.resetTokens.get(token);

      if (!userId || newPassword.length < 8) {
        json(response, 400, {
          error: {
            code: "invalid_reset_token",
            message: "Password reset token is invalid or expired.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      const user = state.users.get(userId);
      if (!user) {
        json(response, 404, {
          error: {
            code: "user_not_found",
            message: "User not found.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      user.password = newPassword;
      state.resetTokens.delete(token);
      json(response, 200, { message: "Password reset complete." });
      return;
    }

    if (request.method === "GET" && pathname === "/api/v1/projects") {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      json(response, 200, {
        items: state.projectOrder
          .map((projectId) => state.projects.get(projectId))
          .filter(Boolean)
          .filter((project) => project.organizationId === user.organizationId)
          .map(projectSummary),
        nextCursor: null,
      });
      return;
    }

    if (request.method === "POST" && pathname === "/api/v1/projects") {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      const payload = await readBody(request);
      const project = {
        id: randomUUID(),
        organizationId: user.organizationId,
        name: String(payload.name ?? "").trim(),
        slug: String(payload.slug ?? "").trim() || `project-${Date.now()}`,
        description: payload.description ? String(payload.description) : null,
        metadata: payload.metadata && typeof payload.metadata === "object" ? payload.metadata : {},
        createdAt: nowIso(),
        updatedAt: nowIso(),
      };

      state.projects.set(project.id, project);
      state.projectOrder.push(project.id);
      json(response, 200, projectSummary(project));
      return;
    }

    const projectMatch = pathname.match(/^\/api\/v1\/projects\/([^/]+)$/);
    if (request.method === "GET" && projectMatch) {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      const project = state.projects.get(projectMatch[1]);
      if (!project || project.organizationId !== user.organizationId) {
        json(response, 404, {
          error: {
            code: "project_not_found",
            message: "Project not found.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      json(response, 200, projectSummary(project));
      return;
    }

    const soilSamplesMatch = pathname.match(/^\/api\/v1\/projects\/([^/]+)\/soil-samples$/);
    if (soilSamplesMatch) {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      const projectId = soilSamplesMatch[1];
      const samples = Array.from(state.soilSamples.values()).filter(
        (sample) => sample.projectId === projectId && sample.organizationId === user.organizationId,
      );

      if (request.method === "GET") {
        json(response, 200, { items: samples.map(sampleSummary), nextCursor: null });
        return;
      }

      if (request.method === "POST") {
        const payload = await readBody(request);
        const sample = {
          id: randomUUID(),
          organizationId: user.organizationId,
          projectId,
          sampleCode: String(payload.sampleCode ?? "").trim(),
          currentVersionId: randomUUID(),
          name: payload.name ? String(payload.name) : null,
          description: payload.description ? String(payload.description) : null,
          collectedOn: payload.collectedOn ? String(payload.collectedOn) : null,
          location:
            payload.location && typeof payload.location === "object" ? payload.location : {},
          measurements:
            payload.measurements && typeof payload.measurements === "object"
              ? payload.measurements
              : {},
          metadata: payload.metadata && typeof payload.metadata === "object" ? payload.metadata : {},
          createdAt: nowIso(),
          updatedAt: nowIso(),
        };

        state.soilSamples.set(sample.id, sample);
        json(response, 200, sampleSummary(sample));
        return;
      }
    }

    const scenariosMatch = pathname.match(/^\/api\/v1\/projects\/([^/]+)\/scenarios$/);
    if (scenariosMatch) {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      const projectId = scenariosMatch[1];
      const scenarios = Array.from(state.scenarios.values()).filter(
        (scenario) =>
          scenario.projectId === projectId && scenario.organizationId === user.organizationId,
      );

      if (request.method === "GET") {
        json(response, 200, { items: scenarios.map(scenarioSummary), nextCursor: null });
        return;
      }

      if (request.method === "POST") {
        const payload = await readBody(request);
        const scenario = {
          id: randomUUID(),
          organizationId: user.organizationId,
          projectId,
          stableKey: randomUUID(),
          name: String(payload.name ?? "").trim(),
          description: payload.description ? String(payload.description) : null,
          soilSampleId: String(payload.soilSampleId ?? ""),
          soilSampleVersionId: randomUUID(),
          foodWebDefinitionId: randomUUID(),
          parameterSetId: randomUUID(),
          scenarioConfig:
            payload.scenarioConfig && typeof payload.scenarioConfig === "object"
              ? payload.scenarioConfig
              : {},
          createdAt: nowIso(),
          updatedAt: nowIso(),
        };

        state.scenarios.set(scenario.id, scenario);
        json(response, 200, scenarioSummary(scenario));
        return;
      }
    }

    if (request.method === "POST" && pathname === "/api/v1/runs") {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      const payload = await readBody(request);
      const scenario = state.scenarios.get(String(payload.scenarioId ?? ""));
      if (!scenario) {
        json(response, 404, {
          error: {
            code: "scenario_not_found",
            message: "Scenario not found.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      const run = {
        id: randomUUID(),
        organizationId: user.organizationId,
        projectId: scenario.projectId,
        scenarioId: scenario.id,
        status: "succeeded",
        engineName: "soil-engine",
        engineVersion: "0.1.0",
        inputSchemaVersion: "1.0.0",
        inputHash: `input-${randomUUID()}`,
        resultHash: `result-${randomUUID()}`,
        queuedAt: nowIso(),
        startedAt: nowIso(),
        completedAt: nowIso(),
        createdAt: nowIso(),
        updatedAt: nowIso(),
        inputSnapshot: {
          projectId: scenario.projectId,
          scenarioId: scenario.id,
          requestedModules:
            payload.executionOptions?.requestedModules ?? ["flux", "mineralization"],
        },
        resultSummary: {
          status: "succeeded",
          score: 91,
          carbonGainPercent: 12.4,
          microbialBalance: "improving",
        },
      };

      state.runs.set(run.id, run);
      state.runsByProject.set(scenario.projectId, run.id);
      json(response, 200, runSummary(run));
      return;
    }

    const runMatch = pathname.match(/^\/api\/v1\/runs\/([^/]+)$/);
    if (request.method === "GET" && runMatch) {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      const run = state.runs.get(runMatch[1]);
      if (!run || run.organizationId !== user.organizationId) {
        json(response, 404, {
          error: {
            code: "run_not_found",
            message: "Run not found.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      json(response, 200, runSummary(run));
      return;
    }

    const runStatusMatch = pathname.match(/^\/api\/v1\/runs\/([^/]+)\/status$/);
    if (request.method === "GET" && runStatusMatch) {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      const run = state.runs.get(runStatusMatch[1]);
      if (!run || run.organizationId !== user.organizationId) {
        json(response, 404, {
          error: {
            code: "run_not_found",
            message: "Run not found.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      json(response, 200, runStatus(run));
      return;
    }

    const runResultsMatch = pathname.match(/^\/api\/v1\/runs\/([^/]+)\/results$/);
    if (request.method === "GET" && runResultsMatch) {
      const user = requireAuth(request, response);
      if (!user) {
        return;
      }

      const run = state.runs.get(runResultsMatch[1]);
      if (!run || run.organizationId !== user.organizationId) {
        json(response, 404, {
          error: {
            code: "run_not_found",
            message: "Run not found.",
            details: {},
            issues: [],
          },
        });
        return;
      }

      json(response, 200, runResults(run));
      return;
    }

    json(response, 404, {
      error: {
        code: "not_found",
        message: `No mock route defined for ${request.method} ${pathname}.`,
        details: {},
        issues: [],
      },
    });
  } catch (error) {
    json(response, 500, {
      error: {
        code: "mock_server_error",
        message: error instanceof Error ? error.message : "Unknown mock server error.",
        details: {},
        issues: [],
      },
    });
  }
});

server.listen(port, "127.0.0.1", () => {
  console.log(`Mock Bio API listening on http://127.0.0.1:${port}`);
});

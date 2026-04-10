import type { JsonObject } from "@bio/api-client";

export function parseJsonObject(value: string, label: string): JsonObject {
  const parsed = JSON.parse(value) as unknown;
  if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
    throw new Error(`${label} must be a JSON object.`);
  }
  return parsed as JsonObject;
}

export function parseJsonValue<T>(value: string): T {
  return JSON.parse(value) as T;
}

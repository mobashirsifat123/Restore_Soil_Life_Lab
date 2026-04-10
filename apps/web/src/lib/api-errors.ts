import { ApiError } from "@bio/api-client";

type ApiErrorEnvelope = {
  error?: {
    message?: string;
    issues?: Array<{
      field?: string;
      message?: string;
    }>;
  };
};

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiError) {
    const body = error.body as ApiErrorEnvelope | null;
    const issues = body?.error?.issues
      ?.map((issue) => {
        if (!issue?.message) {
          return null;
        }

        return issue.field ? `${issue.field}: ${issue.message}` : issue.message;
      })
      .filter(Boolean);

    if (issues?.length) {
      return issues.join(" ");
    }

    if (body?.error?.message) {
      return body.error.message;
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallback;
}

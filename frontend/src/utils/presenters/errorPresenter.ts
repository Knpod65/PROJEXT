export interface NormalizedError {
  titleKey: string;
  descriptionKey: string;
  retryAction: "retry" | "refresh" | "none";
  canRetry: boolean;
}

interface ErrorWithMessageKey {
  message_key?: string | null;
}

export function normalizeApiError(error: unknown): NormalizedError {
  if (error && typeof error === "object" && "message_key" in error) {
    const e = error as ErrorWithMessageKey;
    return {
      titleKey: e.message_key || "errors.generic.title",
      descriptionKey: e.message_key ? `${e.message_key}.description` : "errors.generic.description",
      retryAction: "retry",
      canRetry: true,
    };
  }

  if (error instanceof Error) {
    const msg = error.message.toLowerCase();
    if (msg.includes("network") || msg.includes("fetch")) {
      return {
        titleKey: "errors.network.title",
        descriptionKey: "errors.network.description",
        retryAction: "retry",
        canRetry: true,
      };
    }
    if (msg.includes("permission") || msg.includes("unauthorized")) {
      return {
        titleKey: "errors.permission.title",
        descriptionKey: "errors.permission.description",
        retryAction: "none",
        canRetry: false,
      };
    }
  }

  return {
    titleKey: "errors.generic.title",
    descriptionKey: "errors.generic.description",
    retryAction: "retry",
    canRetry: true,
  };
}

export function getErrorMessageKey(error: unknown): string {
  return normalizeApiError(error).titleKey;
}

export function getErrorDescriptionKey(error: unknown): string {
  return normalizeApiError(error).descriptionKey;
}

export function getRetryActionModel(error: unknown) {
  const n = normalizeApiError(error);
  return { action: n.retryAction, canRetry: n.canRetry };
}

export function getFallbackErrorState(domain: string): NormalizedError {
  return {
    titleKey: `errors.${domain}.title`,
    descriptionKey: `errors.${domain}.description`,
    retryAction: "retry",
    canRetry: true,
  };
}

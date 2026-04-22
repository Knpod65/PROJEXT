import { translate, translateApiMessage } from "@/i18n";

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

type Primitive = string | number | boolean | null | undefined;

interface RequestOptions {
  body?: unknown;
  headers?: HeadersInit;
  signal?: AbortSignal;
  formData?: FormData;
  query?: Record<string, Primitive>;
}

const API_BASE = "/api";

function buildUrl(path: string, query?: Record<string, Primitive>) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${API_BASE}${normalizedPath}`, window.location.origin);

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    });
  }

  return `${url.pathname}${url.search}`;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function readStringField(record: Record<string, unknown>, key: string) {
  const value = record[key];
  return typeof value === "string" && value.trim() ? value : null;
}

function extractErrorMessage(payload: unknown) {
  if (!isRecord(payload)) {
    return null;
  }

  const detail = payload.detail;
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (isRecord(detail)) {
    const detailMessage = readStringField(detail, "message");
    if (detailMessage) {
      return detailMessage;
    }
  }

  return readStringField(payload, "message");
}

async function parseResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }

  if (contentType.includes("text/")) {
    return (await response.text()) as T;
  }

  return (await response.blob()) as T;
}

export async function request<T>(
  method: string,
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, headers, signal, formData, query } = options;
  const url = buildUrl(path, query);
  const init: RequestInit = {
    method,
    credentials: "include",
    headers: headers ?? {},
    signal,
  };

  if (formData) {
    init.body = formData;
  } else if (body !== undefined) {
    init.body = JSON.stringify(body);
    init.headers = {
      "Content-Type": "application/json",
      ...headers,
    };
  }

  const response = await fetch(url, init);
  const payload = await parseResponse<unknown>(response).catch(() => undefined);

  if (!response.ok) {
    const rawDetail = extractErrorMessage(payload);
    const detail = rawDetail
      ? translateApiMessage(rawDetail)
      : translate("errors.requestFailed", { status: response.status });

    if (response.status === 401) {
      window.dispatchEvent(new Event("ems:unauthorized"));
    }

    throw new ApiError(response.status, detail, payload);
  }

  return payload as T;
}

export const get = <T>(path: string, options?: Omit<RequestOptions, "body" | "formData">) =>
  request<T>("GET", path, options);

export const post = <T>(path: string, body?: unknown, options?: Omit<RequestOptions, "body">) =>
  request<T>("POST", path, { ...options, body });

export const put = <T>(path: string, body?: unknown, options?: Omit<RequestOptions, "body">) =>
  request<T>("PUT", path, { ...options, body });

export const del = <T>(path: string, options?: Omit<RequestOptions, "body" | "formData">) =>
  request<T>("DELETE", path, options);

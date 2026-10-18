import { appConfig } from '../../config';
import { STORAGE_KEYS } from '../../constants';
import type { ApiErrorBody, Session } from '../../types';

/** A failed call, with the quanar's code and, for validation, every issue. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly issues: { path: string; message: string }[] = [],
  ) {
    super(message);
  }
}

function token(): string | undefined {
  try {
    return (JSON.parse(localStorage.getItem(STORAGE_KEYS.SESSION) ?? 'null') as Session | null)?.token;
  } catch {
    return undefined;
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {};
  const t = token();
  if (t) headers.Authorization = `Bearer ${t}`;
  if (body !== undefined) headers['Content-Type'] = 'application/json';

  const res = await fetch(`${appConfig.apiUrl}${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  const data = res.status === 204 ? undefined : await res.json().catch(() => undefined);
  if (!res.ok) {
    const e = (data as ApiErrorBody | undefined)?.error;
    throw new ApiError(res.status, e?.code ?? 'unknown', e?.message ?? res.statusText, e?.details?.issues);
  }
  return data as T;
}

/** The one place the client talks HTTP: it adds the token and reads the quanar's errors. */
export const httpClient = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, body ?? {}),
  put: <T>(path: string, body?: unknown) => request<T>('PUT', path, body),
  patch: <T>(path: string, body?: unknown) => request<T>('PATCH', path, body),
};

import { useAuthStore } from '../stores/authStore';

// CORS WORKAROUND (Catalyst AppSail):
// The Catalyst gateway intercepts OPTIONS preflight and strips CORS headers.
// To avoid preflight entirely, we:
// 1. Use Content-Type: text/plain (not application/json) — avoids preflight
// 2. Use httpOnly cookies for auth instead of Authorization header — avoids preflight
// 3. Use POST + X-HTTP-Method-Override header for PUT/DELETE — avoids preflight
// Remove this workaround when a proper CORS solution is available.

const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

interface ApiOptions extends RequestInit {
  json?: unknown;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiFetch<T = unknown>(
  path: string,
  options: ApiOptions = {},
): Promise<T> {
  const { json, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    ...(fetchOptions.headers as Record<string, string>),
  };

  if (json !== undefined) {
    headers['Content-Type'] = 'text/plain';
    fetchOptions.body = JSON.stringify(json);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...fetchOptions,
    headers,
    credentials: 'include',
  });

  if (response.status === 401) {
    useAuthStore.getState().logout();
    window.location.href = '/login';
    throw new ApiError('Unauthorized', 401);
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(body.detail || response.statusText, response.status);
  }

  return response.json();
}

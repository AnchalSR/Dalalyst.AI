const CONFIGURED_API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000';
const API_BASE_KEY = 'dalalyst_api_base';
const TOKEN_KEY = 'dalalyst_token';
const USER_KEY = 'dalalyst_user';

function getApiBaseCandidates() {
  const stored = localStorage.getItem(API_BASE_KEY);
  const candidates = [
    'http://localhost:8001',
    'http://127.0.0.1:8001',
    CONFIGURED_API_BASE,
    stored,
    'http://localhost:8000',
    'http://127.0.0.1:8000',
  ].filter(Boolean);
  return [...new Set(candidates)];
}

function rememberApiBase(base) {
  localStorage.setItem(API_BASE_KEY, base);
}

function forgetApiBase(base) {
  if (localStorage.getItem(API_BASE_KEY) === base) {
    localStorage.removeItem(API_BASE_KEY);
  }
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function persistSession(payload) {
  localStorage.setItem(TOKEN_KEY, payload.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function formatErrorDetail(detail) {
  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item) => item?.msg || item?.message || JSON.stringify(item))
      .join(', ');
  }

  if (detail && typeof detail === 'object') {
    return detail.message || JSON.stringify(detail);
  }

  return 'Request failed.';
}

function shouldRetryWithAnotherBase(status, detail) {
  if (status >= 500) {
    return true;
  }

  const message = typeof detail === 'string' ? detail : formatErrorDetail(detail);
  return message.includes('Failed to load market data for');
}

export async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }

  if (options.auth) {
    const token = getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  const apiBases = getApiBaseCandidates();
  let lastError = null;

  for (const apiBase of apiBases) {
    let response;
    try {
      response = await fetch(`${apiBase}${path}`, {
        method: options.method || 'GET',
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
      });
    } catch (networkError) {
      console.error('API network error:', networkError);
      lastError = new Error(
        `Cannot reach backend at ${apiBase}. Make sure FastAPI is running.`,
      );
      lastError.status = 0;
      continue;
    }

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const payload = isJson ? await response.json() : await response.text();

    if (response.ok) {
      rememberApiBase(apiBase);
      return payload;
    }

    const detail = formatErrorDetail(
      typeof payload === 'string' ? payload : payload?.detail || payload?.message || payload,
    );
    console.error('API error response:', payload || response.statusText);

    if (shouldRetryWithAnotherBase(response.status, detail) && apiBase !== apiBases.at(-1)) {
      forgetApiBase(apiBase);
      lastError = new Error(detail);
      lastError.status = response.status;
      continue;
    }

    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }

  throw lastError || new Error('Request failed.');
}

/**
 * Frontend API configuration.
 *
 * VITE_API_URL is the public backend origin in production. The legacy
 * VITE_API_BASE_URL form is retained as a local/Docker compatibility fallback.
 */
const configuredApiUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const normalizedApiUrl = configuredApiUrl.replace(/\/+$/, '');

export const API_BASE_URL = normalizedApiUrl.endsWith('/api/v1')
  ? normalizedApiUrl
  : `${normalizedApiUrl}/api/v1`;

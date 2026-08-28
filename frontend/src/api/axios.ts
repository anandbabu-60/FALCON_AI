import axios from 'axios';
import { API_BASE_URL } from './config';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('research_access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config as (typeof error.config & { _retry?: boolean }) | undefined;
    const refreshToken = localStorage.getItem('research_refresh_token');
    if (error.response?.status === 401 && request && !request._retry && refreshToken && !String(request.url).includes('/auth/refresh')) {
      request._retry = true;
      try {
        const refreshResponse = await axios.post<{ access_token: string; refresh_token: string }>(`${api.defaults.baseURL}/auth/refresh`, { refresh_token: refreshToken });
        localStorage.setItem('research_access_token', refreshResponse.data.access_token);
        localStorage.setItem('research_refresh_token', refreshResponse.data.refresh_token);
        request.headers.Authorization = `Bearer ${refreshResponse.data.access_token}`;
        return api(request);
      } catch {
        localStorage.removeItem('research_access_token');
        localStorage.removeItem('research_refresh_token');
      }
    }
    if (error.response?.status === 401) localStorage.removeItem('research_access_token');
    return Promise.reject(error);
  },
);

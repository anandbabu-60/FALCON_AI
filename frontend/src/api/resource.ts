import { api } from './axios';

export type Page<T> = { items: T[]; total: number; page: number; size: number };

export function resourceApi<T, C, U = Partial<C>>(basePath: string) {
  return {
    list: (projectId: string, params?: { page?: number; size?: number; search?: string }) => api.get<Page<T>>(`/projects/${projectId}/${basePath}`, { params }),
    get: (projectId: string, id: string) => api.get<T>(`/projects/${projectId}/${basePath}/${id}`),
    create: (projectId: string, payload: C) => api.post<T>(`/projects/${projectId}/${basePath}`, payload),
    update: (projectId: string, id: string, payload: U) => api.patch<T>(`/projects/${projectId}/${basePath}/${id}`, payload),
    remove: (projectId: string, id: string) => api.delete(`/projects/${projectId}/${basePath}/${id}`),
  };
}

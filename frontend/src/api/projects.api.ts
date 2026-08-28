import { api } from './axios';

export type Project = {
	id: string;
	title: string;
	research_idea: string;
	domain: string;
	description: string | null;
	status: 'draft' | 'active' | 'paused' | 'completed' | 'archived';
	created_at: string;
	updated_at: string;
};

export type ProjectPage = { items: Project[]; total: number; page: number; size: number };

export type ProjectCreate = Omit<Project, 'id' | 'created_at' | 'updated_at'>;
export type ProjectUpdate = Partial<ProjectCreate>;

export const listProjects = (params?: { page?: number; size?: number; search?: string; domain?: string; project_status?: Project['status'] }) => api.get<ProjectPage>('/projects', { params });
export const getProject = (projectId: string) => api.get<Project>(`/projects/${projectId}`);
export const createProject = (payload: ProjectCreate) => api.post<Project>('/projects', payload);
export const updateProject = (projectId: string, payload: ProjectUpdate) => api.patch<Project>(`/projects/${projectId}`, payload);
export const deleteProject = (projectId: string) => api.delete(`/projects/${projectId}`);
export const generateProjectRoadmap = (projectId: string) => api.post(`/projects/${projectId}/roadmap/generate`);

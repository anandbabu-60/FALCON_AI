import { createProject, deleteProject, getProject, listProjects, updateProject, type ProjectCreate, type ProjectUpdate } from '../api/projects.api';

export const fetchProjects = (params?: Parameters<typeof listProjects>[0]) => listProjects(params).then((response) => response.data);
export const fetchProject = (projectId: string) => getProject(projectId).then((response) => response.data);
export const addProject = (payload: ProjectCreate) => createProject(payload).then((response) => response.data);
export const editProject = (projectId: string, payload: ProjectUpdate) => updateProject(projectId, payload).then((response) => response.data);
export const removeProject = (projectId: string) => deleteProject(projectId);

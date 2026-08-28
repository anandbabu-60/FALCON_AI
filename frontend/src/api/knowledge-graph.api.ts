import { api } from './axios';

export type GraphNode = { id: string; title?: string; name?: string; description?: string | null; abstract?: string | null };
export type ProjectGraph = { project: GraphNode; papers: GraphNode[]; authors: GraphNode[]; themes: GraphNode[]; gaps: GraphNode[] };
export const getGraphHealth = () => api.get('/knowledge-graph/health');
export const getProjectGraph = (projectId: string) => api.get<ProjectGraph>(`/knowledge-graph/project/${projectId}`);
export const syncProjectGraph = (projectId: string) => api.post(`/knowledge-graph/project/${projectId}/sync`);
export const syncProjectNode = (project_id: string, title: string, description?: string | null) => api.post('/knowledge-graph/project', { project_id, title, description });
export const syncPaperNode = (project_id: string, paper_id: string, title: string, authors?: string, abstract?: string) => api.post('/knowledge-graph/paper', { project_id, paper_id, title, authors, abstract });
export const addTheme = (project_id: string, paper_id: string, theme: string) => api.post('/knowledge-graph/theme', { project_id, paper_id, theme });
export const addGap = (project_id: string, gap_title: string) => api.post('/knowledge-graph/gap', { project_id, gap_title });

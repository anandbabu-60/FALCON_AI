import { addGap, addTheme, getGraphHealth, getProjectGraph, syncPaperNode, syncProjectNode } from '../api/knowledge-graph.api';

export const graphHealth = () => getGraphHealth().then((response) => response.data);
export const fetchProjectGraph = (projectId: string) => getProjectGraph(projectId).then((response) => response.data);
export const syncProject = (projectId: string, title: string, description?: string | null) => syncProjectNode(projectId, title, description);
export const syncPaper = (projectId: string, paperId: string, title: string, authors?: string, abstract?: string) => syncPaperNode(projectId, paperId, title, authors, abstract);
export const createTheme = (projectId: string, paperId: string, theme: string) => addTheme(projectId, paperId, theme);
export const createGap = (projectId: string, gapTitle: string) => addGap(projectId, gapTitle);

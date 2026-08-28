import { api } from './axios';

export type AIEvidence = { id: string; title: string; year?: number | null; url?: string | null; doi?: string | null; snippet?: string };
export type AIRelatedPaper = { id: string; title: string; year?: number | null; url?: string | null; doi?: string | null; abstract?: string };
export type AIChatResponse = { answer: string; sources?: string[]; evidence?: AIEvidence[]; related_papers?: AIRelatedPaper[]; research_gaps?: string[]; suggestions?: string[]; project_id?: string | null; artifact_id?: string | null };
export type PaperSearchResult = { external_id?: string | null; title: string; authors?: string | null; abstract?: string | null; doi?: string | null; publication?: string | null; year?: number | null; url?: string | null; pdf_url?: string | null; source: string };
export type ResearchCollectionResponse = AIChatResponse & { items?: PaperSearchResult[]; saved_count?: number };
export type AIResultResponse<T> = { success: boolean; result: T; artifact_id?: string | null };
export type AIWorkflowResponse = AIResultResponse<Record<string, unknown>> & { research_topic: string; persisted: Record<string, number> };
export type AIQuestionResponse = { answer: string; citations: { id: number; source: string; page: number | string; distance: number }[]; citation_validation: { valid: boolean; cited_evidence: number[]; invalid_evidence: number[] } };

export const chat = (message: string, project_id?: string) => api.post<AIChatResponse>('/ai/chat', { message, project_id });
export const ask = (query: string, project_id?: string, top_k = 5) => api.post<AIQuestionResponse>('/ai/ask', { query, project_id, top_k });
export const researchSources = (topic: string, project_id?: string, limit = 10, save_results = false) => api.post<ResearchCollectionResponse>('/ai/research-sources', { topic, project_id, limit, save_results });
export const analyzePaper = (title: string, abstract: string, project_id?: string) => api.post<AIResultResponse<Record<string, unknown>>>('/ai/analyze-paper', { title, abstract, project_id });
export const analyzeThemes = (papers: string[], project_id?: string) => api.post<AIResultResponse<Record<string, unknown>>>('/ai/analyze-themes', { papers, project_id });
export const analyzeGaps = (research_topic: string, paper_analyses: string[], theme_analysis: string, project_id?: string) => api.post<AIResultResponse<Record<string, unknown>>>('/ai/analyze-gaps', { research_topic, paper_analyses, theme_analysis, project_id });
export const runWorkflow = (research_topic: string, papers: Record<string, unknown>[], project_id?: string) => api.post<AIWorkflowResponse>('/ai/workflow', { research_topic, papers, project_id });
export const listAIArtifacts = (projectId: string, params?: { page?: number; size?: number }) => api.get<{ items: Record<string, unknown>[]; total: number; page: number; size: number }>(`/projects/${projectId}/ai-artifacts`, { params });
export const recommendDatasets = (projectId: string) => api.post<{ items: Record<string, unknown>[]; saved_count: number; provider: string }>('/ai/recommend-datasets', { project_id: projectId });
export const recommendTools = (projectId: string) => api.post<{ items: Record<string, unknown>[]; saved_count: number; provider: string }>('/ai/recommend-tools', { project_id: projectId });
export const generateCitations = (projectId: string) => api.post<{ items: Record<string, unknown>[]; created_count: number; paper_count: number }>('/ai/generate-citations', { project_id: projectId });

import { analyzeGaps, analyzePaper, analyzeThemes, ask, chat, researchSources, runWorkflow, type AIWorkflowResponse, type ResearchCollectionResponse } from '../api/ai.api';
import { uploadDocument } from '../api/documents.api';

export type AIChatResponse = import('../api/ai.api').AIChatResponse;
export type { ResearchCollectionResponse } from '../api/ai.api';

export async function askResearchCopilot(message: string, projectId?: string): Promise<AIChatResponse> {
  const response = await chat(message, projectId);
  return response.data;
}

export async function askResearchEvidence(query: string, projectId?: string) {
  const response = await ask(query, projectId);
  return response.data;
}

export async function collectResearchSources(topic: string, projectId?: string, limit = 10, saveResults = false): Promise<ResearchCollectionResponse> {
  const response = await researchSources(topic, projectId, limit, saveResults);
  return response.data;
}

export async function analyzeResearchPaper(title: string, abstract: string, projectId?: string) {
  const response = await analyzePaper(title, abstract, projectId);
  return response.data;
}

export async function analyzeResearchThemes(papers: string[], projectId?: string) {
  const response = await analyzeThemes(papers, projectId);
  return response.data;
}

export async function analyzeResearchGaps(topic: string, paperAnalyses: string[], themeAnalysis: string, projectId?: string) {
  const response = await analyzeGaps(topic, paperAnalyses, themeAnalysis, projectId);
  return response.data;
}

export async function generateResearchWorkflow(topic: string, papers: Record<string, unknown>[], projectId?: string) {
  const response = await runWorkflow(topic, papers, projectId);
  return response.data as AIWorkflowResponse;
}

export async function uploadResearchDocument(file: File, projectId?: string): Promise<{ answer: string; document_id?: string }> {
  if (!projectId) throw new Error('Create or select a project before uploading a document.');
  const response = await uploadDocument(projectId, file);
  const document = response.data;
  return { document_id: document.id, answer: `${document.file_name} was extracted successfully (${document.page_count} page${document.page_count === 1 ? '' : 's'}).${document.indexed ? ' It is now searchable by the research copilot.' : ''}` };
}

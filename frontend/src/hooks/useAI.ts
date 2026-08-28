import { useState } from 'react';
import { chat, researchSources, runWorkflow, type AIChatResponse, type ResearchCollectionResponse } from '../api/ai.api';

export function useAI(projectId?: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const execute = async <T,>(request: Promise<{ data: T }>) => { setLoading(true); setError(null); try { return (await request).data; } catch { setError('AI request failed. Check your provider configuration.'); throw new Error('AI request failed'); } finally { setLoading(false); } };
  return {
    loading,
    error,
    chat: (message: string) => execute<AIChatResponse>(chat(message, projectId)),
    researchSources: (topic: string) => execute<ResearchCollectionResponse>(researchSources(topic, projectId)),
    workflow: (topic: string, papers: Record<string, unknown>[]) => execute(runWorkflow(topic, papers, projectId)),
  };
}

export default useAI;

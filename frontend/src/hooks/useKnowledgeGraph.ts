import { useCallback, useEffect, useState } from 'react';
import { type ProjectGraph } from '../api/knowledge-graph.api';
import { fetchProjectGraph } from '../services/knowledgeGraph.service';

export function useKnowledgeGraph(projectId?: string) {
  const [graph, setGraph] = useState<ProjectGraph | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reload = useCallback(async () => { if (!projectId) { setGraph(null); return; } setLoading(true); try { setGraph(await fetchProjectGraph(projectId)); setError(null); } catch { setError('Knowledge graph is unavailable'); } finally { setLoading(false); } }, [projectId]);
  useEffect(() => { void reload(); }, [reload]);
  return { graph, loading, error, reload };
}

export default useKnowledgeGraph;

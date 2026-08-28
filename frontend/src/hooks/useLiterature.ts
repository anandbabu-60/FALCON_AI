import { useCallback, useEffect, useState } from 'react';
import { type Page } from '../api/resource';
import { type Paper } from '../api/literature.api';
import { fetchPapers } from '../services/literature.service';

export function useLiterature(projectId?: string) {
  const [page, setPage] = useState<Page<Paper> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reload = useCallback(async () => {
    if (!projectId) { setPage(null); return; }
    setLoading(true); try { setPage(await fetchPapers(projectId, { size: 100 })); setError(null); } catch { setError('Unable to load literature'); } finally { setLoading(false); }
  }, [projectId]);
  useEffect(() => { void reload(); }, [reload]);
  return { page, papers: page?.items ?? [], loading, error, reload };
}

export default useLiterature;

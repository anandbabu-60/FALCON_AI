import { useCallback, useEffect, useState } from 'react';
import { type Project, type ProjectCreate, type ProjectUpdate } from '../api/projects.api';
import { addProject, editProject, fetchProjects, removeProject } from '../services/project.service';

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const reload = useCallback(async () => { setLoading(true); try { const page = await fetchProjects({ size: 100 }); setProjects(page.items); setError(null); } catch { setError('Unable to load projects'); } finally { setLoading(false); } }, []);
  useEffect(() => { void reload(); }, [reload]);
  const create = async (payload: ProjectCreate) => { const item = await addProject(payload); setProjects((items) => [item, ...items]); return item; };
  const update = async (id: string, payload: ProjectUpdate) => { const item = await editProject(id, payload); setProjects((items) => items.map((project) => project.id === id ? item : project)); return item; };
  const remove = async (id: string) => { await removeProject(id); setProjects((items) => items.filter((project) => project.id !== id)); };
  return { projects, loading, error, reload, create, update, remove };
}

export default useProjects;

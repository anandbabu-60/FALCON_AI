import { papersApi, type PaperPayload } from '../api/literature.api';

export const fetchPapers = (projectId: string, params?: Parameters<typeof papersApi.list>[1]) => papersApi.list(projectId, params).then((response) => response.data);
export const addPaper = (projectId: string, payload: PaperPayload) => papersApi.create(projectId, payload).then((response) => response.data);
export const editPaper = (projectId: string, paperId: string, payload: Partial<PaperPayload>) => papersApi.update(projectId, paperId, payload).then((response) => response.data);
export const removePaper = (projectId: string, paperId: string) => papersApi.remove(projectId, paperId);

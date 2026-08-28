import { api } from './axios';

export type DocumentStatus = 'uploaded' | 'processing' | 'ready' | 'failed';
export type ResearchDocument = { id: string; project_id: string; file_name: string; content_type: string; page_count: number; chunk_count: number; indexed: boolean; status: DocumentStatus; error_message: string | null; created_at: string; updated_at: string };
export type DocumentPage = { items: ResearchDocument[]; total: number; page: number; size: number };

export const listDocuments = (projectId: string, params?: { page?: number; size?: number }) => api.get<DocumentPage>(`/projects/${projectId}/documents`, { params });
export const uploadDocument = (projectId: string, file: File) => { const data = new FormData(); data.append('file', file); return api.post<ResearchDocument>(`/projects/${projectId}/documents`, data); };
export const getDocumentText = (projectId: string, documentId: string) => api.get<ResearchDocument & { extracted_text: string | null }>(`/projects/${projectId}/documents/${documentId}`);

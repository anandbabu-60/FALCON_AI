import { resourceApi } from './resource';
export type Paper = { id: string; title: string; authors: string | null; abstract: string | null; doi: string | null; publication: string | null; year: number | null; url: string | null; summary: string | null; keywords: string | null; created_at: string; updated_at: string };
export type PaperPayload = Omit<Paper, 'id' | 'created_at' | 'updated_at'>;
export const papersApi = resourceApi<Paper, PaperPayload>('papers');

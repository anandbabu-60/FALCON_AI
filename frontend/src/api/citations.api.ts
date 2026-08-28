import { resourceApi } from './resource';
export type Citation = { id: string; apa: string | null; ieee: string | null; bibtex: string | null; mla: string | null; ris: string | null; paper_id: string | null; created_at: string; updated_at: string };
export type CitationPayload = Omit<Citation, 'id' | 'created_at' | 'updated_at'>;
export const citationsApi = resourceApi<Citation, CitationPayload>('citations');

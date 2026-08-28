import { resourceApi } from './resource';
export type ResearchGap = { id: string; problem: string; existing_solution: string | null; limitation: string | null; research_gap: string; proposed_innovation: string | null; created_at: string; updated_at: string };
export type ResearchGapPayload = Omit<ResearchGap, 'id' | 'created_at' | 'updated_at'>;
export const gapsApi = resourceApi<ResearchGap, ResearchGapPayload>('gaps');

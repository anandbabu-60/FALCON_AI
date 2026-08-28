import { resourceApi } from './resource';
export type Tool = { id: string; name: string; category: string | null; official_website: string | null; description: string | null; license: string | null; created_at: string; updated_at: string };
export type ToolPayload = Omit<Tool, 'id' | 'created_at' | 'updated_at'>;
export const toolsApi = resourceApi<Tool, ToolPayload>('tools');

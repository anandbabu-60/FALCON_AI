import { resourceApi } from './resource';
export type Dataset = { id: string; name: string; description: string | null; source: string | null; download_link: string | null; license: string | null; size: string | null; domain: string | null; created_at: string; updated_at: string };
export type DatasetPayload = Omit<Dataset, 'id' | 'created_at' | 'updated_at'>;
export const datasetsApi = resourceApi<Dataset, DatasetPayload>('datasets');

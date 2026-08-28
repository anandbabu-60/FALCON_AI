import { resourceApi } from './resource';
export type Experiment = { id: string; methodology: string; algorithms: string | null; evaluation_metrics: string | null; workflow: string | null; expected_results: string | null; created_at: string; updated_at: string };
export type ExperimentPayload = Omit<Experiment, 'id' | 'created_at' | 'updated_at'>;
export const experimentsApi = resourceApi<Experiment, ExperimentPayload>('experiments');

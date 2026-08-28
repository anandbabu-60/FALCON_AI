import { resourceApi } from './resource';
import { api } from './axios';
export type RoadmapStatus = 'pending' | 'in_progress' | 'completed' | 'blocked';
export type RoadmapEntry = { id: string; week_number: number; task: string; deadline: string | null; status: RoadmapStatus; remarks: string | null; created_at: string; updated_at: string };
export type RoadmapPayload = Omit<RoadmapEntry, 'id' | 'created_at' | 'updated_at'>;
export const roadmapApi = resourceApi<RoadmapEntry, RoadmapPayload>('roadmap');
export type RoadmapReminder = { id: string; project_id: string; week_number: number; task: string; deadline: string; status: RoadmapStatus; kind: 'overdue' | 'due_today' | 'upcoming'; message: string };
export const getRoadmapReminders = (projectId: string) => api.get<{ items: RoadmapReminder[]; total: number }>(`/projects/${projectId}/roadmap/reminders`);

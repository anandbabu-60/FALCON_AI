import { resourceApi } from './resource';
export type ApprovalStatus = 'pending' | 'approved' | 'changes_requested';
export type SupervisorReview = { id: string; supervisor_name: string; comments: string | null; approval_status: ApprovalStatus; meeting_date: string | null; suggestions: string | null; created_at: string; updated_at: string };
export type SupervisorReviewPayload = Omit<SupervisorReview, 'id' | 'created_at' | 'updated_at'>;
export const supervisorApi = resourceApi<SupervisorReview, SupervisorReviewPayload>('reviews');

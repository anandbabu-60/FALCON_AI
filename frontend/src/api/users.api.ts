import { api } from './axios';

export type User = {
  id: string;
  email: string;
  full_name: string;
  institution: string | null;
  is_active: boolean;
};

export const getCurrentUser = () => api.get<User>('/users/me');
export const updateCurrentUser = (payload: Partial<Pick<User, 'full_name' | 'institution'>>) => api.patch<User>('/users/me', payload);
export const deleteCurrentUser = () => api.delete('/users/me');

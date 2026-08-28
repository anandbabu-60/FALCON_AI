import { api } from './axios';

export type TokenPair = {
	access_token: string;
	refresh_token: string;
	token_type: string;
};

export type RegisterPayload = {
	email: string;
	full_name: string;
	password: string;
	confirm_password: string;
	institution?: string;
};

export type LoginPayload = {
	email: string;
	password: string;
};

export const register = (payload: RegisterPayload) => api.post('/auth/register', payload);
export const login = (payload: LoginPayload) => api.post<TokenPair>('/auth/login', payload);
export const verifyEmail = (email: string, code: string) => api.post('/auth/verify-email', { email, code });
export const resendVerificationOtp = (email: string) => api.post('/auth/resend-verification-otp', { email });
export const forgotPassword = (email: string) => api.post<{ message: string }>('/auth/forgot-password', { email });
export const resetPassword = (payload: { email: string; code: string; new_password: string; confirm_password: string }) => api.post<{ message: string }>('/auth/reset-password', payload);
export const logout = () => api.post('/auth/logout');

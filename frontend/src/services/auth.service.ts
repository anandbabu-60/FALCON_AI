import { login, logout, register, resendVerificationOtp, verifyEmail, type LoginPayload, type RegisterPayload, type TokenPair } from '../api/auth.api';
import { deleteCurrentUser, getCurrentUser, updateCurrentUser, type User } from '../api/users.api';

export const ACCESS_TOKEN_KEY = 'research_access_token';
export const REFRESH_TOKEN_KEY = 'research_refresh_token';

export function setTokens(tokens: TokenPair) {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);

export async function signIn(payload: LoginPayload) {
  const { data } = await login(payload);
  setTokens(data);
  return data;
}

export const signUp = (payload: RegisterPayload) => register(payload);
export const confirmEmail = (email: string, code: string) => verifyEmail(email, code);
export const resendCode = (email: string) => resendVerificationOtp(email);
export const profile = () => getCurrentUser().then((response) => response.data);
export const updateProfile = (payload: Partial<Pick<User, 'full_name' | 'institution'>>) => updateCurrentUser(payload).then((response) => response.data);
export const deleteAccount = () => deleteCurrentUser();
export async function signOut() {
  try { await logout(); } finally { clearTokens(); }
}

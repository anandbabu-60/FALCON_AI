import type { TokenPair } from '../api/auth.api';
import type { User } from '../api/users.api';
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, clearTokens, setTokens } from '../services/auth.service';

export type AuthSnapshot = { user: User | null; accessToken: string | null };
export const readAuthSnapshot = (): AuthSnapshot => ({ user: null, accessToken: localStorage.getItem(ACCESS_TOKEN_KEY) });
export const persistAuthTokens = (tokens: TokenPair) => setTokens(tokens);
export const resetAuth = () => clearTokens();
export const authKeys = { access: ACCESS_TOKEN_KEY, refresh: REFRESH_TOKEN_KEY } as const;

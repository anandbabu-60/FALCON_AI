import { useCallback, useEffect, useState } from 'react';
import { type LoginPayload } from '../api/auth.api';
import { type User } from '../api/users.api';
import { clearTokens, profile, signIn } from '../services/auth.service';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!localStorage.getItem('research_access_token')) { setLoading(false); return null; }
    try { const current = await profile(); setUser(current); setError(null); return current; }
    catch { clearTokens(); setUser(null); return null; }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const login = useCallback(async (payload: LoginPayload) => {
    setLoading(true); setError(null);
    try { await signIn(payload); return await refresh(); }
    catch (cause) { const message = (cause as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Unable to sign in'; setError(message); throw cause; }
    finally { setLoading(false); }
  }, [refresh]);

  const logout = useCallback(() => { clearTokens(); setUser(null); }, []);
  return { user, loading, error, login, logout, refresh, isAuthenticated: Boolean(user) };
}

export default useAuth;

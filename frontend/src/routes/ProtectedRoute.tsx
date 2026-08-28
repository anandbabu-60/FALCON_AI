import { useEffect } from 'react';
import type { ReactNode } from 'react';
import useAuth from '../hooks/useAuth';

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { loading, isAuthenticated } = useAuth();
  useEffect(() => {
    if (!loading && !isAuthenticated) window.location.replace('/login');
  }, [loading, isAuthenticated]);
  if (loading) return <main className="auth-page"><section className="auth-form-wrap"><p className="auth-subtitle">Checking your session…</p></section></main>;
  return isAuthenticated ? <>{children}</> : null;
}

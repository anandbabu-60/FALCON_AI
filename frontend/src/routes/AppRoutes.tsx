import ResearchApp, { type ResearchScreen } from '../components/ResearchApp';
import Login from '../pages/auth/Login';
import Register from '../pages/auth/Register';
import ForgotPassword from '../pages/auth/ForgotPassword';
import { useEffect, useState } from 'react';
import ProtectedRoute from './ProtectedRoute';

const screens: Record<string, ResearchScreen> = {
  '/dashboard': 'overview', '/projects': 'projects', '/literature': 'literature',
  '/datasets': 'datasets', '/tools': 'tools', '/research-gaps': 'gaps', '/experiments': 'experiments',
  '/citations': 'citations', '/roadmap': 'roadmap', '/knowledge-graph': 'graph', '/documents': 'documents', '/supervisor': 'supervisor', '/settings': 'settings',
};

function OAuthCallback() {
  const [error, setError] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newName, setNewName] = useState('');
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const fragment = new URLSearchParams(window.location.hash.replace(/^#/, ''));
    const accessToken = fragment.get('access_token') || params.get('access_token');
    const refreshToken = fragment.get('refresh_token') || params.get('refresh_token');
    if (accessToken && refreshToken) {
      localStorage.setItem('research_access_token', accessToken);
      localStorage.setItem('research_refresh_token', refreshToken);
      window.history.replaceState({}, document.title, '/oauth/callback');
      window.location.replace('/dashboard');
      return;
    }
    if (params.get('needs_registration') === '1' && params.get('email')) {
      setNewEmail(params.get('email') || '');
      setNewName(params.get('name') || '');
      return;
    }
    setError(params.get('error') || 'Google sign-in could not be completed.');
  }, []);

  return <main className="auth-page"><section className="auth-form-wrap"><div className="auth-form-box"><p className="eyebrow">Google sign-in</p>{newEmail ? <><h2>Create your account.</h2><p className="auth-subtitle">No account exists for <strong>{newEmail}</strong>. Create one to continue.</p><button className="auth-submit" type="button" onClick={() => { window.location.href = `/register?email=${encodeURIComponent(newEmail)}&name=${encodeURIComponent(newName)}`; }}>Create account with this email <span aria-hidden="true">→</span></button><button className="auth-link" type="button" onClick={() => { window.location.href = '/login'; }}>Return to sign in</button></> : error ? <><h2>Sign-in unavailable</h2><p className="auth-error">{error}</p><button className="auth-submit" type="button" onClick={() => { window.location.href = '/login'; }}>Return to sign in</button></> : <h2>Signing you in…</h2>}</div></section></main>;
}

export default function AppRoutes() {
  const path = window.location.pathname.replace(/\/$/, '') || '/';
  if (path === '/' || path === '/login') return <Login />;
  if (path === '/register') return <Register />;
  if (path === '/forgot-password') return <ForgotPassword />;
  if (path === '/oauth/callback') return <OAuthCallback />;
  return <ProtectedRoute><ResearchApp initialScreen={screens[path] ?? 'overview'} /></ProtectedRoute>;
}

import { useEffect, useState } from 'react';
import { ArrowRight, BrainCircuit, Check, Eye, EyeOff, LockKeyhole, Mail, Sparkles } from 'lucide-react';
import { login } from '../../api/auth.api';
import { API_BASE_URL } from '../../api/config';
import './login.css';

export default function Login() {
	const [showPassword, setShowPassword] = useState(false);
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState('');
	const [submitting, setSubmitting] = useState(false);
	useEffect(() => {
		if (localStorage.getItem('research_access_token')) window.location.replace('/dashboard');
	}, []);
	const continueWithGoogle = () => {
		window.location.href = `${API_BASE_URL}/auth/google/login`;
	};

	const submit = async (event: React.FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		if (!email || !password) {
			setError('Enter your email and password to continue.');
			return;
		}
		try {
			setSubmitting(true);
			const { data } = await login({ email, password });
			localStorage.setItem('research_access_token', data.access_token);
			localStorage.setItem('research_refresh_token', data.refresh_token);
			window.location.href = '/dashboard';
		} catch (requestError) {
			const detail = (requestError as { response?: { data?: { detail?: unknown } } }).response?.data?.detail;
			if (typeof detail === 'string') setError(detail);
			else if (detail && typeof detail === 'object' && typeof (detail as { message?: unknown }).message === 'string') setError((detail as { message: string }).message);
			else setError('Sign in failed. Check your email and password, then try again.');
		} finally { setSubmitting(false); }
	};

	return <main className="auth-page"><section className="auth-visual"><div className="auth-brand"><span><Sparkles size={17} /></span> thesis<span>flow</span></div><div className="auth-message"><p className="eyebrow">Your research, understood</p><h1>Make the next question <em>count.</em></h1><p>One intelligent workspace for the papers, gaps, datasets, and experiments behind your thesis.</p></div><div className="auth-orbit" aria-hidden="true"><div className="auth-core"><BrainCircuit size={30} /><span>AI</span></div><i className="auth-ring ring-one" /><i className="auth-ring ring-two" /><span className="auth-node node-one"><Check size={14} /></span><span className="auth-node node-two"><LockKeyhole size={14} /></span><span className="auth-node node-three"><Sparkles size={14} /></span></div><div className="auth-proof"><span className="proof-check"><Check size={13} /></span><span>Research intelligence for focused minds</span></div></section><section className="auth-form-wrap"><div className="auth-form-box"><p className="eyebrow">Welcome back</p><h2>Continue your research.</h2><p className="auth-subtitle">Sign in to return to your research workspace.</p><form onSubmit={submit}><label>Email address<div className="auth-input"><Mail size={16} /><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></div></label><label>Password<div className="auth-input"><LockKeyhole size={16} /><input type={showPassword ? 'text' : 'password'} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Your password" /><button type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button></div></label><div className="auth-options"><label className="remember"><input type="checkbox" defaultChecked /> <span>Remember me</span></label><button type="button" className="auth-link" onClick={() => { window.location.href = '/forgot-password'; }}>Forgot password?</button></div>{error && <p className="auth-error">{error}</p>}<button className="auth-submit" type="submit" disabled={submitting}>{submitting ? 'Signing in…' : 'Sign in'} {!submitting && <ArrowRight size={16} />}</button></form><div className="auth-divider"><span>or continue with</span></div><button className="google-button" type="button" onClick={continueWithGoogle}><strong>G</strong> Continue with Google</button><p className="auth-switch">New to thesisflow? <button className="auth-link" type="button" onClick={() => { window.location.href = '/register'; }}>Create an account</button></p></div><p className="auth-legal">By continuing, you agree to our Terms of Service and Privacy Policy.</p></section></main>;
}

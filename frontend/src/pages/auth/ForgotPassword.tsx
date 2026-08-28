import { useState } from "react";
import { ArrowRight, LockKeyhole, Mail, Sparkles } from "lucide-react";
import { forgotPassword, resetPassword } from "../../api/auth.api";
import "./login.css";

function errorMessage(error: unknown, fallback: string) {
  const detail = (error as { response?: { data?: { detail?: unknown } } }).response?.data?.detail;
  return typeof detail === "string" ? detail : fallback;
}

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [sent, setSent] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const requestCode = async (event: React.FormEvent) => {
    event.preventDefault(); setError(""); setNotice(""); setSaving(true);
    try { const response = await forgotPassword(email.trim()); setSent(true); setNotice(response.data.message); }
    catch (requestError) { setError(errorMessage(requestError, "Unable to send a reset code.")); }
    finally { setSaving(false); }
  };
  const reset = async (event: React.FormEvent) => {
    event.preventDefault();
    if (password.length < 8) { setError("Password must be at least 8 characters."); return; }
    if (password !== confirm) { setError("Passwords do not match."); return; }
    setError(""); setNotice(""); setSaving(true);
    try { const response = await resetPassword({ email: email.trim(), code, new_password: password, confirm_password: confirm }); setNotice(response.data.message); window.setTimeout(() => { window.location.href = "/login"; }, 1000); }
    catch (requestError) { setError(errorMessage(requestError, "Unable to reset your password.")); }
    finally { setSaving(false); }
  };
  return <main className="auth-page"><section className="auth-visual"><div className="auth-brand"><span><Sparkles size={17} /></span> thesis<span>flow</span></div><div className="auth-message"><p className="eyebrow">Secure access</p><h1>Return to your <em>research.</em></h1><p>Reset your password securely and continue building your research workspace.</p></div></section><section className="auth-form-wrap"><div className="auth-form-box"><p className="eyebrow">Account recovery</p><h2>{sent ? "Set a new password." : "Forgot your password?"}</h2><p className="auth-subtitle">{sent ? `Enter the 6-digit code sent to ${email}.` : "We will send a time-limited verification code to your email."}</p>{!sent ? <form onSubmit={requestCode}><label>Email address<div className="auth-input"><Mail size={16} /><input type="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></div></label>{error && <p className="auth-error">{error}</p>}<button className="auth-submit" disabled={saving}>Send reset code <ArrowRight size={16} /></button></form> : <form onSubmit={reset}><label>Verification code<div className="auth-input"><Mail size={16} /><input required inputMode="numeric" maxLength={6} value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, "").slice(0, 6))} placeholder="123456" /></div></label><label>New password<div className="auth-input"><LockKeyhole size={16} /><input required type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="At least 8 characters" /></div></label><label>Confirm new password<div className="auth-input"><LockKeyhole size={16} /><input required type="password" value={confirm} onChange={(event) => setConfirm(event.target.value)} placeholder="Repeat your password" /></div></label>{notice && <p className="auth-success">{notice}</p>}{error && <p className="auth-error">{error}</p>}<button className="auth-submit" disabled={saving || code.length !== 6}>{saving ? "Resetting…" : "Reset password"} <ArrowRight size={16} /></button></form>}{notice && !sent && <p className="auth-success">{notice}</p>}<p className="auth-switch"><button className="auth-link" type="button" onClick={() => { window.location.href = "/login"; }}>Back to sign in</button></p></div><p className="auth-legal">Your reset code expires after 10 minutes.</p></section></main>;
}

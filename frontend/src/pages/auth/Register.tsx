import { useEffect, useState } from "react";
import {
  ArrowRight,
  BrainCircuit,
  Check,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  Sparkles,
  UserRound,
} from "lucide-react";
import {
  register,
  resendVerificationOtp,
  verifyEmail,
} from "../../api/auth.api";
import "./login.css";

export default function Register() {
  const oauthParams = new URLSearchParams(window.location.search);
  const [name, setName] = useState(() => oauthParams.get("name") || "");
  const [email, setEmail] = useState(() => oauthParams.get("email") || "");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [otpMode, setOtpMode] = useState(false);
  const [otp, setOtp] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(300);
  const [resendSeconds, setResendSeconds] = useState(0);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    if (!otpMode) return;
    const timer = window.setInterval(
      () => setSecondsLeft((value) => Math.max(0, value - 1)),
      1000,
    );
    return () => window.clearInterval(timer);
  }, [otpMode]);
  useEffect(() => {
    if (!resendSeconds) return;
    const timer = window.setInterval(
      () => setResendSeconds((value) => Math.max(0, value - 1)),
      1000,
    );
    return () => window.clearInterval(timer);
  }, [resendSeconds]);
  const apiError = (requestError: unknown) =>
    (requestError as { response?: { data?: { detail?: string } } }).response
      ?.data?.detail;
  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim() || !email.trim()) {
      setError("Add your name and a valid email.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    try {
      setSaving(true);
      await register({
        email,
        full_name: name,
        password,
        confirm_password: confirmPassword,
      });
      setOtpMode(true);
      setSecondsLeft(300);
      setResendSeconds(60);
      setNotice("We sent a 6-digit verification code to your email.");
    } catch (requestError) {
      setError(
        apiError(requestError) ||
          "Account creation failed. Check your details and try again.",
      );
    } finally { setSaving(false); }
    }
  };
  const verify = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setSaving(true);
      await verifyEmail(email, otp);
      setNotice("Email verified successfully! Redirecting to login...");
      window.setTimeout(() => {
        window.location.href = "/login";
      }, 800);
    } catch (requestError) {
      setError(
        apiError(requestError) ||
          "OTP verification failed. Please enter the correct OTP.",
      );
    } finally { setSaving(false); }
    }
  };
  const resend = async () => {
    if (resendSeconds > 0) {
      setError(
        `Please wait ${resendSeconds} seconds before requesting another OTP.`,
      );
      return;
    }
    try {
      setSaving(true);
      await resendVerificationOtp(email);
      setSecondsLeft(300);
      setResendSeconds(60);
      setOtp("");
      setNotice("New OTP sent successfully.");
    } catch (requestError) {
      setError(apiError(requestError) || "Unable to resend OTP.");
    } finally { setSaving(false); }
  };
  if (otpMode) {
    const time = `${String(Math.floor(secondsLeft / 60)).padStart(2, "0")}:${String(secondsLeft % 60).padStart(2, "0")}`;
    return (
      <main className="auth-page">
        <section className="auth-form-wrap">
          <div className="auth-form-box">
            <p className="eyebrow">Secure your workspace</p>
            <h2>Verify your email.</h2>
            <p className="auth-subtitle">We sent a 6-digit code to {email}.</p>
            <form onSubmit={verify}>
              <label>
                Verification code
                <div className="auth-input">
                  <Mail size={16} />
                  <input
                    autoFocus
                    inputMode="numeric"
                    maxLength={6}
                    value={otp}
                    onChange={(event) =>
                      setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))
                    }
                    placeholder="123456"
                  />
                </div>
              </label>
              <p className="auth-subtitle">OTP expires in {time}</p>
              {notice && <p className="auth-success">{notice}</p>}
              {error && <p className="auth-error">{error}</p>}
              <button
                className="primary-button"
                type="submit"
                disabled={saving || otp.length !== 6}
              >
                Verify email <ArrowRight size={17} />
              </button>
              <button
                className="auth-link"
                type="button"
                onClick={() => void resend()}
              >
                Resend OTP {resendSeconds ? `(${resendSeconds}s)` : ""}
              </button>
            </form>
          </div>
        </section>
      </main>
    );
  }
  return (
    <main className="auth-page">
      <section className="auth-visual">
        <div className="auth-brand">
          <span>
            <Sparkles size={17} />
          </span>{" "}
          thesis<span>flow</span>
        </div>
        <div className="auth-message">
          <p className="eyebrow">A better way to begin</p>
          <h1>
            Your next <em>breakthrough</em> starts here.
          </h1>
          <p>
            Build a research practice that keeps your best ideas, evidence, and
            momentum together.
          </p>
        </div>
        <div className="auth-orbit" aria-hidden="true">
          <div className="auth-core">
            <BrainCircuit size={30} />
            <span>AI</span>
          </div>
          <i className="auth-ring ring-one" />
          <i className="auth-ring ring-two" />
          <span className="auth-node node-one">
            <Check size={14} />
          </span>
          <span className="auth-node node-two">
            <LockKeyhole size={14} />
          </span>
          <span className="auth-node node-three">
            <Sparkles size={14} />
          </span>
        </div>
        <div className="auth-proof">
          <span className="proof-check">
            <Check size={13} />
          </span>
          <span>Free workspace for your research journey</span>
        </div>
      </section>
      <section className="auth-form-wrap">
        <div className="auth-form-box">
          <p className="eyebrow">Create your workspace</p>
          <h2>Start with an idea.</h2>
          <p className="auth-subtitle">
            Create your account and bring your research into focus.
          </p>
          <form onSubmit={submit}>
            <label>
              Your name
              <div className="auth-input">
                <UserRound size={16} />
                <input
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Alex Researcher"
                />
              </div>
            </label>
            <label>
              Email address
              <div className="auth-input">
                <Mail size={16} />
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@example.com"
                />
              </div>
            </label>
            <label>
              Password
              <div className="auth-input">
                <LockKeyhole size={16} />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="At least 8 characters"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((value) => !value)}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </label>
            <label>
              Confirm password
              <div className="auth-input">
                <LockKeyhole size={16} />
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="Confirm password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword((value) => !value)}
                >
                  {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </label>
            {error && <p className="auth-error">{error}</p>}
            <button className="auth-submit" type="submit" disabled={saving}>
              {saving ? "Creating account…" : "Create account"} {!saving && <ArrowRight size={16} />}
            </button>
          </form>
          <p className="auth-switch">
            Already have an account?{" "}
            <button
              className="auth-link"
              type="button"
              onClick={() => {
                window.location.href = "/login";
              }}
            >
              Sign in
            </button>
          </p>
        </div>
        <p className="auth-legal">
          By continuing, you agree to our Terms of Service and Privacy Policy.
        </p>
      </section>
    </main>
  );
}

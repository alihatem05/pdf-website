import { useState } from "react";
import "./login.css";

function LoginPage({ onNavigate }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    setSubmitted(true);
  }

  return (
    <div className="min-h-screen center-xy px-4">
      <div className="w-full max-w-md">
        <div className="wordmark">
          <span className="brand">Lumen</span>
        </div>

        <div className="card">
          <h1 className="title">Welcome back</h1>
          <p className="subtitle">Sign in to your account to continue.</p>

          {submitted ? (
            <div className="submitted-note">
              Signed in as <strong>{email}</strong>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="form">
              <div className="form-row">
                <label htmlFor="login-email">Email</label>
                <input
                  id="login-email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="input"
                />
              </div>

              <div className="form-row">
                <label htmlFor="login-password">Password</label>
                <input
                  id="login-password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input"
                />
              </div>

              <div className="checkbox-row">
                <button
                  type="button"
                  aria-pressed={remember}
                  onClick={() => setRemember(!remember)}
                  className={`checkbox ${remember ? "checked" : ""}`}
                >
                  {remember && (
                    <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                      <path d="M1 4L3.5 6.5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  )}
                </button>
                <label onClick={() => setRemember(!remember)} className="muted-note" style={{ margin: 0 }}>
                  Remember me
                </label>
              </div>

              <button type="submit" className="btn btn-primary">
                Sign in
              </button>
            </form>
          )}
        </div>

        <p className="muted-note">
          {"Don't have an account?"} <button onClick={() => onNavigate("register")} className="link-button">Register</button>
        </p>
      </div>
    </div>
  );
}

  export default LoginPage;

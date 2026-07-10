import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRegister } from "../../hooks/useAuth";
import "./register.css";

function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const navigate = useNavigate();
  const { submitRegister, isLoading, error } = useRegister();

  const isFormValid = username.trim() !== "" && email.trim() !== "" && password.trim() !== "";

  async function handleSubmit(e) {
    e.preventDefault();
    const ok = await submitRegister(username, email, password, remember);
    if (ok) {
      navigate("/dashboard");
    }
  }

  return (
    <div className="min-h-screen center-xy px-4">
      <div className="w-full max-w-md">
        <div className="wordmark-register">
          <span className="brand">Doclify</span>
        </div>

        <div className="card">
          <h1 className="title">Create an account</h1>
          <p className="subtitle">Get started — it only takes a moment.</p>

          <form onSubmit={handleSubmit} className="form">
            <div className="form-row">
              <label htmlFor="reg-username">Username</label>
              <input
                id="reg-username"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="yourname"
                className="input"
              />
            </div>

            <div className="form-row">
              <label htmlFor="reg-email">Email</label>
              <input
                id="reg-email"
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
              <label htmlFor="reg-password">Password</label>
              <input
                id="reg-password"
                type="password"
                autoComplete="new-password"
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

            {error ? <p className="submitted-note">{error}</p> : null}

            <button type="submit" className="btn btn-primary" disabled={!isFormValid || isLoading}>
              {isLoading ? "Creating account..." : "Create account"}
            </button>
          </form>
        </div>

        <p className="muted-note">
          Already have an account? {" "}<button onClick={() => navigate("/login")} className="link-button">Sign in</button>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;

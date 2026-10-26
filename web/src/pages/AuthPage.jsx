import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function AuthPage({ mode }) {
  const isSignup = mode === "signup";
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (isSignup && password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setSubmitting(true);
    try {
      if (isSignup) await signup(email, password);
      else await login(email, password);
      navigate("/");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Something went wrong. Please check your details and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1 style={{ fontSize: "1.5rem" }}>{isSignup ? "Create your account" : "Welcome back"}</h1>

        {error && <p className="error">{error}</p>}

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete={isSignup ? "new-password" : "current-password"}
        />

        <button type="submit" className="auth-submit" disabled={submitting}>
          {submitting ? "Please wait..." : isSignup ? "Sign up" : "Log in"}
        </button>

        <p className="auth-switch">
          {isSignup ? (
            <>Already have an account? <Link to="/login">Log in</Link></>
          ) : (
            <>New here? <Link to="/signup">Create an account</Link></>
          )}
        </p>
      </form>
    </div>
  );
}

export default AuthPage;

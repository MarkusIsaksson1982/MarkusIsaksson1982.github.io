import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";
import styles from "./LoginPage.module.css";

const USERNAME_PATTERN = /^[a-zA-Z0-9]+$/;

function LoginPage() {
  const navigate = useNavigate();
  const { login, register, isAuthenticated } = useAuth();
  const [mode, setMode] = useState("login");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    username: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [feedback, setFeedback] = useState("");

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/tasks", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const validate = () => {
    const nextErrors = {};
    const username = form.username.trim();

    if (username.length < 3 || username.length > 30) {
      nextErrors.username = "Username must be 3-30 characters.";
    } else if (!USERNAME_PATTERN.test(username)) {
      nextErrors.username = "Username must be alphanumeric.";
    }

    if (form.password.length < 8) {
      nextErrors.password = "Password must be at least 8 characters.";
    }

    if (mode === "register" && form.confirmPassword !== form.password) {
      nextErrors.confirmPassword = "Passwords do not match.";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleModeChange = (nextMode) => {
    setMode(nextMode);
    setErrors({});
    setFeedback("");
    setForm({
      username: form.username,
      password: "",
      confirmPassword: "",
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFeedback("");
    if (!validate()) {
      return;
    }

    setLoading(true);
    try {
      const payload = {
        username: form.username.trim().toLowerCase(),
        password: form.password,
      };
      if (mode === "login") {
        await login(payload);
      } else {
        await register(payload);
      }
      navigate("/tasks", { replace: true });
    } catch (requestError) {
      if (requestError.status === 429) {
        const retryAfter = requestError.retryAfter ?? 60;
        setFeedback(`Too many attempts. Try again in ${retryAfter} second(s).`);
      } else {
        setFeedback(requestError.message ?? "Authentication failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className={`card ${styles.card}`} aria-labelledby="auth-title">
      <header className={styles.header}>
        <h2 id="auth-title">{mode === "login" ? "Sign In" : "Create Account"}</h2>
        <p>Use demo credentials: username <code>demo</code>, password <code>demo1234</code>.</p>
      </header>

      <div className={styles.modeToggle} role="tablist" aria-label="Authentication mode">
        <button
          type="button"
          role="tab"
          aria-selected={mode === "login"}
          className={mode === "login" ? styles.modeActive : styles.modeButton}
          onClick={() => handleModeChange("login")}
        >
          Login
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === "register"}
          className={mode === "register" ? styles.modeActive : styles.modeButton}
          onClick={() => handleModeChange("register")}
        >
          Register
        </button>
      </div>

      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        <div className={styles.field}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            name="username"
            type="text"
            value={form.username}
            onChange={handleChange}
            autoComplete="username"
            required
          />
          {errors.username && (
            <p className={styles.error} role="alert">
              {errors.username}
            </p>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            required
          />
          {errors.password && (
            <p className={styles.error} role="alert">
              {errors.password}
            </p>
          )}
        </div>

        {mode === "register" && (
          <div className={styles.field}>
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={form.confirmPassword}
              onChange={handleChange}
              autoComplete="new-password"
              required
            />
            {errors.confirmPassword && (
              <p className={styles.error} role="alert">
                {errors.confirmPassword}
              </p>
            )}
          </div>
        )}

        {feedback && (
          <p className={styles.feedback} role="alert">
            {feedback}
          </p>
        )}

        <button className={styles.submit} type="submit" disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Login" : "Register"}
        </button>
      </form>
    </section>
  );
}

export default LoginPage;

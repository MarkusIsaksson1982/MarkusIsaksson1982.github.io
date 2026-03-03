import { useEffect } from "react";
import { HashRouter, NavLink, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import ThemeToggle from "./components/ThemeToggle.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import TasksPage from "./pages/TasksPage.jsx";
import AnalyticsPage from "./pages/AnalyticsPage.jsx";
import styles from "./App.module.css";

function AppChrome() {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <header className={styles.header}>
        <div className={`container ${styles.headerInner}`}>
          <div className={styles.brand}>
            <h1 className={styles.title}>MP4</h1>
            <p className={styles.subtitle}>Secure REST Simulator</p>
          </div>
          <nav aria-label="Primary navigation" className={styles.nav}>
            {isAuthenticated && (
              <>
                <NavLink
                  to="/tasks"
                  className={({ isActive }) => `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`}
                >
                  Tasks
                </NavLink>
                <NavLink
                  to="/analytics"
                  className={({ isActive }) => `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`}
                >
                  Analytics
                </NavLink>
              </>
            )}
          </nav>
          <ThemeToggle />
        </div>
      </header>
      <main className={styles.main} id="main-content" tabIndex={-1}>
        <div className="container">
          <Routes>
            <Route path="/" element={<Navigate to={isAuthenticated ? "/tasks" : "/login"} replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/tasks"
              element={
                <ProtectedRoute>
                  <TasksPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <AnalyticsPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </main>
    </>
  );
}

function App() {
  useEffect(() => {
    if (!("serviceWorker" in navigator)) {
      return;
    }

    const baseUrl = import.meta.env.BASE_URL || "/";
    const swUrl = `${baseUrl}sw.js`;

    const registerWorker = async () => {
      try {
        await navigator.serviceWorker.register(swUrl, {
          type: "module",
          scope: baseUrl,
        });
      } catch (error) {
        console.error("Service worker registration failed:", error);
      }
    };

    void registerWorker();
  }, []);

  return (
    <HashRouter>
      <AuthProvider>
        <AppChrome />
      </AuthProvider>
    </HashRouter>
  );
}

export default App;

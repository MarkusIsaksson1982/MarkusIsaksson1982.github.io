import { useTheme } from '../../context/ThemeContext';
import styles from './Header.module.css';

/**
 * Header — site identity, FCC profile link, theme toggle.
 * Reads from ThemeContext only (not AppContext) — isolates re-renders.
 */
export default function Header() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className={styles.header} role="banner">
      <div className={styles.inner}>
        <hgroup className={styles.identity}>
          <h1 className={styles.name}>Markus Isaksson</h1>
          <p className={styles.sub}>FCC Certification Explorer · 3,600+ Verified Hours · React 18</p>
        </hgroup>
        <div className={styles.actions}>
          <a
            href="https://www.freecodecamp.org/fccfb1888e4-715c-408f-9fcb-887123f4d08b"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.fccLink}
            aria-label="View FCC profile on freeCodeCamp (opens in new tab)"
          >
            FCC Profile ↗
          </a>
          <button
            className={styles.themeToggle}
            onClick={toggleTheme}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            aria-pressed={isDark}
          >
            <span aria-hidden="true">{isDark ? '☀️' : '🌙'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import { ThemeProvider } from './context/ThemeContext';
import { AppProvider } from './context/AppContext';

/**
 * Mount order is intentional:
 *
 * StrictMode → In dev, renders components twice to expose impure renders
 *              and side effects. Remove for production profiling only.
 *
 * ThemeProvider → Must be outermost so it can set <html data-theme>
 *                 before any child renders. Prevents flash of wrong theme.
 *
 * AppProvider → Inside Theme; has no dependency on ThemeContext.
 *               Owns filter state, modal state, notes.
 *
 * Two contexts rather than one: Theme changes (frequent) should not
 * force AppContext consumers to re-render, and vice versa.
 */
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <AppProvider>
        <App />
      </AppProvider>
    </ThemeProvider>
  </StrictMode>
);

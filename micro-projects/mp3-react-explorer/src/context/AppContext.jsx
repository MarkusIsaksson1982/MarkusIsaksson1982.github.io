import { createContext, useContext, useReducer, useMemo, useEffect } from 'react';
import { useLocalStorage } from '../hooks/useLocalStorage';

/** @type {React.Context<{ state: AppState, dispatch: React.Dispatch<any> } | null>} */
const AppContext = createContext(null);

/**
 * @typedef {{
 *   query: string,
 *   category: string,
 *   activeTags: Set<string>,
 *   openSlug: string | null,
 *   notes: Record<string, string>
 * }} AppState
 */

/** @type {AppState} */
const BASE_INITIAL_STATE = {
  query: '',
  category: 'all',
  activeTags: new Set(),
  openSlug: null,
  notes: {},
};

/**
 * reducer — pure function, mirrors MP1's dispatch/reducer pattern.
 *
 * KEY RULE: Must return a new object on every action (React uses Object.is comparison).
 * Mutating state directly would cause React to skip re-renders.
 *
 * Sets require special care: always create new Set() from existing —
 * mutating an existing Set and returning the same reference won't trigger re-render.
 *
 * @param {AppState} state
 * @param {{ type: string, payload?: any }} action
 * @returns {AppState}
 */
function reducer(state, action) {
  switch (action.type) {
    case 'SET_QUERY':
      return { ...state, query: action.payload };

    case 'SET_CATEGORY':
      return { ...state, category: action.payload };

    case 'TOGGLE_TAG': {
      const next = new Set(state.activeTags); // New Set — new reference ✓
      next.has(action.payload) ? next.delete(action.payload) : next.add(action.payload);
      return { ...state, activeTags: next };
    }

    case 'OPEN_MODAL':
      return { ...state, openSlug: action.payload };

    case 'CLOSE_MODAL':
      return { ...state, openSlug: null };

    case 'SAVE_NOTE':
      return {
        ...state,
        notes: {
          ...state.notes, // New object — new reference ✓
          [action.payload.slug]: action.payload.text,
        },
      };

    case 'CLEAR_FILTERS':
      // Preserve notes — user data must survive filter resets
      return { ...BASE_INITIAL_STATE, notes: state.notes };

    default:
      return state;
  }
}

export function AppProvider({ children }) {
  // Read persisted notes from localStorage on mount
  const [savedNotes] = useLocalStorage('mp3-notes', {});

  const [state, dispatch] = useReducer(reducer, {
    ...BASE_INITIAL_STATE,
    notes: savedNotes,
  });

  /**
   * Persist notes to localStorage as a side effect of state changes.
   * NOT done inside the reducer (reducers must be pure, no side effects).
   * useEffect runs after render — safe, won't block the UI.
   */
  useEffect(() => {
    try {
      localStorage.setItem('mp3-notes', JSON.stringify(state.notes));
    } catch (e) {
      console.warn('AppContext: could not persist notes', e);
    }
  }, [state.notes]);

  /**
   * Stable context value.
   * Note: dispatch from useReducer is guaranteed stable by React —
   * it won't change between renders. Including it in useMemo deps
   * is correct (it satisfies exhaustive-deps) and has zero cost.
   */
  const value = useMemo(() => ({ state, dispatch }), [state, dispatch]);

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

/**
 * useAppState — safe AppContext consumer with guard clause.
 */
export function useAppState() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppState must be used inside <AppProvider>');
  return ctx;
}

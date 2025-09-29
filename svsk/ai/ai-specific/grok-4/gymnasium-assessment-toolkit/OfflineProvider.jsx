import React, { createContext, useContext } from 'react';
import Dexie from 'dexie';

const db = new Dexie("AssessmentDB");
db.version(1).stores({ rubrics: 'id' });

const OfflineContext = createContext();

export const OfflineProvider = ({ children }) => {
  // Save/load/clear from chain
  return <OfflineContext.Provider value={{}}>{children}</OfflineContext.Provider>;
};

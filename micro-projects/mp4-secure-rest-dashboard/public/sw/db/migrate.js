export const DB_NAME = "mp4_secure_rest_simulator";
export const DB_VERSION = 1;

function ensureStore(db, tx, storeName, options) {
  if (db.objectStoreNames.contains(storeName)) {
    return tx.objectStore(storeName);
  }
  return db.createObjectStore(storeName, options);
}

function ensureIndex(store, name, keyPath, options = {}) {
  if (store.indexNames.contains(name)) {
    return;
  }
  store.createIndex(name, keyPath, options);
}

export function migrateDatabase(db, tx, oldVersion, _newVersion) {
  if (oldVersion < 1) {
    const usersStore = ensureStore(db, tx, "users", { keyPath: "id" });
    ensureIndex(usersStore, "username", "username", { unique: true });

    const tasksStore = ensureStore(db, tx, "tasks", { keyPath: "id" });
    ensureIndex(tasksStore, "user_id", "user_id");
    ensureIndex(tasksStore, "user_status", ["user_id", "status"]);
    ensureIndex(tasksStore, "user_created", ["user_id", "created_at"]);

    const auditStore = ensureStore(db, tx, "audit_log", { keyPath: "id" });
    ensureIndex(auditStore, "user_timestamp", ["user_id", "timestamp"]);
  }
}

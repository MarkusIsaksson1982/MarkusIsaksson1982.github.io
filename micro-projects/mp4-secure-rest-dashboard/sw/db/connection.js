import { DB_NAME, DB_VERSION, migrateDatabase } from "./migrate.js";

function waitForTransaction(tx) {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error ?? new Error("IndexedDB transaction failed"));
    tx.onabort = () => reject(tx.error ?? new Error("IndexedDB transaction aborted"));
  });
}

function requestToPromise(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("IndexedDB request failed"));
  });
}

function cursorToArray(source, { range, direction = "next" } = {}) {
  return new Promise((resolve, reject) => {
    const output = [];
    const request = source.openCursor(range, direction);
    request.onsuccess = () => {
      const cursor = request.result;
      if (!cursor) {
        resolve(output);
        return;
      }
      output.push(cursor.value);
      cursor.continue();
    };
    request.onerror = () => reject(request.error ?? new Error("Cursor iteration failed"));
  });
}

export class IndexedDBConnection {
  constructor({ name = DB_NAME, version = DB_VERSION } = {}) {
    this.name = name;
    this.version = version;
    this._db = null;
    this._openPromise = null;
  }

  async open() {
    if (this._db) {
      return this._db;
    }
    if (this._openPromise) {
      return this._openPromise;
    }

    this._openPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(this.name, this.version);

      request.onupgradeneeded = (event) => {
        const db = request.result;
        migrateDatabase(db, request.transaction, event.oldVersion, event.newVersion ?? this.version);
      };

      request.onsuccess = () => {
        this._db = request.result;
        this._db.onversionchange = () => {
          this._db?.close();
          this._db = null;
          this._openPromise = null;
        };
        resolve(this._db);
      };

      request.onerror = () => reject(request.error ?? new Error("Failed to open IndexedDB"));
      request.onblocked = () => reject(new Error("IndexedDB open blocked by another tab"));
    });

    try {
      return await this._openPromise;
    } catch (error) {
      this._openPromise = null;
      throw error;
    }
  }

  async get(storeName, key) {
    return this.transaction([storeName], "readonly", async (stores) =>
      requestToPromise(stores[storeName].get(key)),
    );
  }

  async getAll(storeName, { index, range, direction = "next" } = {}) {
    return this.transaction([storeName], "readonly", async (stores) => {
      const store = stores[storeName];
      const source = index ? store.index(index) : store;
      return cursorToArray(source, { range, direction });
    });
  }

  async put(storeName, record) {
    return this.transaction([storeName], "readwrite", async (stores) =>
      requestToPromise(stores[storeName].put(record)),
    );
  }

  async delete(storeName, key) {
    return this.transaction([storeName], "readwrite", async (stores) =>
      requestToPromise(stores[storeName].delete(key)),
    );
  }

  async transaction(stores, mode, callback) {
    const db = await this.open();
    const tx = db.transaction(stores, mode);
    const txDone = waitForTransaction(tx);
    const storeMap = Object.fromEntries(stores.map((name) => [name, tx.objectStore(name)]));

    try {
      const result = await callback(storeMap, tx);
      await txDone;
      return result;
    } catch (error) {
      try {
        tx.abort();
        await txDone.catch(() => {});
      } catch {
        // Ignore abort errors; the transaction may already be closed.
      }
      throw error;
    }
  }
}

export function createDatabaseConnection(options) {
  return new IndexedDBConnection(options);
}

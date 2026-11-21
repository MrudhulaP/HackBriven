import { openDB, DBSchema, IDBPDatabase } from 'idb';
import { OfflineQueueItem, Customer } from '../types';

interface BolKhataDB extends DBSchema {
  offline_queue: {
    key: string;
    value: OfflineQueueItem;
    indexes: { 'by-status': string };
  };
  cached_customers: {
    key: string;
    value: Customer;
  };
}

const DB_NAME = 'bolkhata_offline_db';
const DB_VERSION = 1;

let dbPromise: Promise<IDBPDatabase<BolKhataDB>> | null = null;

export function getDB() {
  if (!dbPromise) {
    dbPromise = openDB<BolKhataDB>(DB_NAME, DB_VERSION, {
      upgrade(db) {
        const queueStore = db.createObjectStore('offline_queue', { keyPath: 'operation_id' });
        queueStore.createIndex('by-status', 'status');

        db.createObjectStore('cached_customers', { keyPath: 'id' });
      },
    });
  }
  return dbPromise;
}

export async function addOfflineQueueItem(item: OfflineQueueItem): Promise<void> {
  const db = await getDB();
  await db.put('offline_queue', item);
}

export async function getPendingOfflineItems(): Promise<OfflineQueueItem[]> {
  const db = await getDB();
  const all = await db.getAll('offline_queue');
  return all.filter(i => i.status === 'SAVED_LOCALLY' || i.status === 'PENDING_SYNC');
}

export async function updateOfflineItemStatus(operation_id: string, status: OfflineQueueItem['status']): Promise<void> {
  const db = await getDB();
  const item = await db.get('offline_queue', operation_id);
  if (item) {
    item.status = status;
    await db.put('offline_queue', item);
  }
}

export async function cacheCustomers(customers: Customer[]): Promise<void> {
  const db = await getDB();
  const tx = db.transaction('cached_customers', 'readwrite');
  for (const c of customers) {
    await tx.store.put(c);
  }
  await tx.done;
}

export async function getCachedCustomers(): Promise<Customer[]> {
  const db = await getDB();
  return db.getAll('cached_customers');
}

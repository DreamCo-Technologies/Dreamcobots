import pg from "pg";

interface ReadinessClient {
  connect(): Promise<unknown>;
  query(text: string): Promise<unknown>;
  end(): Promise<void>;
}

// A dedicated connection can be closed on timeout without returning an active
// query to the application pool or terminating another request's connection.
export function createDatabaseReadinessProbe(
  createClient: () => ReadinessClient = () => new pg.Client({
    connectionString: process.env.DATABASE_URL,
    connectionTimeoutMillis: 1500,
    query_timeout: 1500,
  }),
) {
  return async (signal: AbortSignal) => {
    const client = createClient();
    let closing: Promise<void> | undefined;
    const close = () => closing ??= client.end().catch(() => {});
    const abort = () => { void close(); };
    const assertActive = () => {
      if (signal.aborted) throw new Error("Database readiness probe aborted");
    };
    signal.addEventListener("abort", abort, { once: true });
    try {
      assertActive();
      await client.connect();
      assertActive();
      await client.query("SELECT 1");
      assertActive();
    } finally {
      signal.removeEventListener("abort", abort);
      await close();
    }
  };
}

export const probeDatabaseConnection = createDatabaseReadinessProbe();

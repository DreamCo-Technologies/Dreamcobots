import pg from "pg";
import { Socket } from "node:net";

interface ReadinessClient {
  connect(): Promise<unknown>;
  query(text: string): Promise<unknown>;
  end(): Promise<void>;
}

// A dedicated connection can be closed on timeout without returning an active
// query to the application pool or terminating another request's connection.
export function createDatabaseReadinessProbe(
  createClient: () => ReadinessClient = () => {
    const socket = new Socket();
    const client = new pg.Client({
      connectionString: process.env.DATABASE_URL,
      connectionTimeoutMillis: 1500,
      query_timeout: 1500,
      stream: () => socket,
    });
    return {
      connect: () => client.connect(),
      query: text => client.query(text),
      end: async () => {
        // Mark intentional shutdown before destroying the owned socket. This
        // also bounds cleanup if the peer never acknowledges a graceful end.
        const ending = client.end();
        socket.destroy();
        await ending;
      },
    };
  },
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

// ---------------------------------------------------------------------------
// Batch processing with Server-Sent Events (SSE)
// ---------------------------------------------------------------------------

export interface BatchItem {
  name: string;
  content: string;
  type: string;
}

export interface BatchOptions {
  retries?: number;
  minTimeout?: number;
}

type SendEventFn = (event: { type: string; [key: string]: unknown }) => void;
type ProcessorFn = (item: BatchItem) => Promise<string>;

/**
 * Process a list of items sequentially with retry logic, emitting SSE events
 * for each item's start, success, and failure.
 */
export async function batchProcessWithSSE(
  items: BatchItem[],
  processor: ProcessorFn,
  sendEvent: SendEventFn,
  options: BatchOptions = {},
): Promise<void> {
  const { retries = 2, minTimeout = 1000 } = options;

  sendEvent({ type: "batch_start", total: items.length });

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    sendEvent({ type: "item_start", index: i, name: item.name, total: items.length });

    let lastError: Error | null = null;
    let result: string | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        result = await processor(item);
        break;
      } catch (err: any) {
        lastError = err instanceof Error ? err : new Error(String(err));
        if (attempt < retries) {
          const delay = minTimeout * Math.pow(2, attempt);
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }

    if (result !== null) {
      sendEvent({ type: "item_complete", index: i, name: item.name, output: result });
    } else {
      sendEvent({
        type: "item_error",
        index: i,
        name: item.name,
        error: lastError?.message ?? "Unknown error",
      });
    }
  }

  sendEvent({ type: "batch_complete", total: items.length });
}

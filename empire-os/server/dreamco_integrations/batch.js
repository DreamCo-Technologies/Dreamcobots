// ---------------------------------------------------------------------------
// Batch processing with Server-Sent Events (SSE)
// ---------------------------------------------------------------------------
/**
 * Process a list of items sequentially with retry logic, emitting SSE events
 * for each item's start, success, and failure.
 */
export async function batchProcessWithSSE(items, processor, sendEvent, options = {}) {
    const { retries = 2, minTimeout = 1000 } = options;
    sendEvent({ type: "batch_start", total: items.length });
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        sendEvent({ type: "item_start", index: i, name: item.name, total: items.length });
        let lastError = null;
        let result = null;
        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                result = await processor(item);
                break;
            }
            catch (err) {
                lastError = err instanceof Error ? err : new Error(String(err));
                if (attempt < retries) {
                    const delay = minTimeout * Math.pow(2, attempt);
                    await new Promise((resolve) => setTimeout(resolve, delay));
                }
            }
        }
        if (result !== null) {
            sendEvent({ type: "item_complete", index: i, name: item.name, output: result });
        }
        else {
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

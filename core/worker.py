"""
DreamCo Worker — Queue-based bot execution worker.

Workers pull bot jobs from a RedisQueueBus and execute them via the
BotExecutor / DreamCoOrchestrator, enabling parallelised processing.

Usage
-----
    from core.worker import BotWorker
    from event_bus.redis_bus import RedisQueueBus

    queue = RedisQueueBus()
    worker = BotWorker(queue=queue)

    # Enqueue a job
    queue.enqueue({"bot_path": "bots.real_estate_bot.real_estate_bot", "bot_name": "real_estate_bot"})

    # Process one job (blocks if timeout > 0)
    result = worker.process_one(timeout=5)

    # Run continuously (blocking)
    worker.run_forever()
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from core.dreamco_orchestrator import DreamCoOrchestrator
from event_bus.redis_bus import RedisQueueBus


# ---------------------------------------------------------------------------
# BotWorker
# ---------------------------------------------------------------------------


class BotWorker:
    """
    Single worker that polls a job queue and executes bot jobs.

    Parameters
    ----------
    queue : RedisQueueBus
        Queue to read jobs from.
    orchestrator : DreamCoOrchestrator | None
        Orchestrator used to run bots.  A new instance is created if
        ``None`` is provided.
    poll_timeout : int
        Seconds to block on dequeue (0 = non-blocking poll).
    max_jobs : int | None
        Stop after processing this many jobs (``None`` = run forever).
    """

    def __init__(
        self,
        queue: Optional[RedisQueueBus] = None,
        orchestrator: Optional[DreamCoOrchestrator] = None,
        poll_timeout: int = 2,
        max_jobs: Optional[int] = None,
    ) -> None:
        self.queue = queue or RedisQueueBus()
        self.orchestrator = orchestrator or DreamCoOrchestrator()
        self.poll_timeout = poll_timeout
        self.max_jobs = max_jobs

        self._results: List[Dict[str, Any]] = []
        self._jobs_processed: int = 0
        self._running: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_one(self, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """
        Dequeue and execute one bot job.

        Parameters
        ----------
        timeout : int
            Seconds to wait for a job.

        Returns
        -------
        dict | None
            Execution result, or ``None`` if the queue was empty.
        """
        job = self.queue.dequeue(timeout=timeout)
        if job is None:
            return None

        bot_path: str = job.get("bot_path", "")
        bot_name: str = job.get("bot_name", bot_path)

        result = self.orchestrator.run_bot(bot_path, bot_name)
        self._results.append(result)
        self._jobs_processed += 1
        return result

    def run_forever(self) -> None:
        """
        Poll the queue and execute jobs until stopped.

        Runs synchronously.  Call :meth:`stop` from another thread to
        terminate the loop gracefully.
        """
        self._running = True
        while self._running:
            if self.max_jobs is not None and self._jobs_processed >= self.max_jobs:
                break
            result = self.process_one(timeout=self.poll_timeout)
            if result is None and self.poll_timeout == 0:
                # Non-blocking mode: nothing in queue, yield
                break

    def stop(self) -> None:
        """Signal :meth:`run_forever` to stop after the current job."""
        self._running = False

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def jobs_processed(self) -> int:
        """Total number of jobs processed by this worker."""
        return self._jobs_processed

    def get_results(self) -> List[Dict[str, Any]]:
        """Return all results collected so far."""
        return list(self._results)

    def summary(self) -> Dict[str, Any]:
        """Aggregate summary of all results processed by this worker."""
        return self.orchestrator.summary(self._results)


# ---------------------------------------------------------------------------
# WorkerPool — runs N workers in parallel threads
# ---------------------------------------------------------------------------


class WorkerPool:
    """
    Pool of :class:`BotWorker` threads for parallelised bot processing.

    Parameters
    ----------
    size : int
        Number of worker threads.
    queue : RedisQueueBus | None
        Shared queue; created if ``None``.
    max_jobs_per_worker : int | None
        Cap per worker (``None`` = unlimited).
    """

    def __init__(
        self,
        size: int = 4,
        queue: Optional[RedisQueueBus] = None,
        max_jobs_per_worker: Optional[int] = None,
    ) -> None:
        self.size = size
        self.queue = queue or RedisQueueBus()
        self._workers: List[BotWorker] = [
            BotWorker(queue=self.queue, max_jobs=max_jobs_per_worker)
            for _ in range(size)
        ]
        self._threads: List[threading.Thread] = []

    def start(self) -> None:
        """Launch all worker threads."""
        for worker in self._workers:
            t = threading.Thread(target=worker.run_forever, daemon=True)
            t.start()
            self._threads.append(t)

    def stop(self) -> None:
        """Signal all workers to stop."""
        for worker in self._workers:
            worker.stop()

    def join(self, timeout: Optional[float] = None) -> None:
        """Wait for all worker threads to finish."""
        for t in self._threads:
            t.join(timeout=timeout)

    def total_jobs_processed(self) -> int:
        """Return the combined job count across all workers."""
        return sum(w.jobs_processed for w in self._workers)

    def all_results(self) -> List[Dict[str, Any]]:
        """Return results from all workers combined."""
        results = []
        for w in self._workers:
            results.extend(w.get_results())
        return results

'use strict';

/**
 * DreamCo — Job Queue
 *
 * Simple in-memory FIFO queue that prevents bots from colliding or
 * overloading memory when many bots fire at once.
 *
 * Usage:
 *   const { addJob, runQueue } = require('./queue');
 *   addJob(async () => await myBot.run());
 *   await runQueue();
 */

/** @type {Array<() => Promise<any>>} */
const _queue = [];

let _running = false;

/**
 * Add a job (async function) to the queue.
 * @param {() => Promise<any>} job
 */
function addJob(job) {
  if (typeof job !== 'function') {
    throw new Error('Job must be a function');
  }
  _queue.push(job);
}

/**
 * Drain the queue, executing each job sequentially.
 * If the queue is already draining, this call waits for it to finish
 * before starting a new drain pass (ensuring no jobs are silently lost).
 *
 * @returns {Promise<Array<{status: 'fulfilled'|'rejected', value?: any, reason?: any}>>}
 */
async function runQueue() {
  // Wait for any in-progress run to finish before starting a new one
  while (_running) {
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  _running = true;

  const results = [];

  while (_queue.length > 0) {
    const job = _queue.shift();
    try {
      const value = await job();
      results.push({ status: 'fulfilled', value });
    } catch (err) {
      results.push({ status: 'rejected', reason: err.message });
    }
  }

  _running = false;
  return results;
}

/**
 * Current queue depth.
 * @returns {number}
 */
function size() {
  return _queue.length;
}

/**
 * Clear the queue (useful in tests or emergency stop).
 */
function clear() {
  _queue.length = 0;
  _running = false;
}

module.exports = { addJob, runQueue, size, clear };

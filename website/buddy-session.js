/* Browser-local coordination only. Never an authentication or execution receipt. */
(function (root) {
  'use strict';
  if (root.BuddySession) return;
  const key = 'buddy.ui.session.v1';
  const allowed = new Set(['context.updated', 'action.proposed', 'action.failed']);
  const surfaces = new Set(['issues', 'agents', 'pulls', 'control']);
  const listeners = new Set();
  let storage = true;
  let state;
  try { state = JSON.parse(root.localStorage.getItem(key) || 'null'); } catch (_) { storage = false; }
  if (!state || typeof state.id !== 'string' || !Array.isArray(state.events)) {
    state = { id: root.crypto.randomUUID(), events: [] };
  }
  function snapshot() { return JSON.parse(JSON.stringify({ ...state, storage, scope: 'browser_local_only', runtime_verified: false })); }
  function emit(type, surface) {
    if (!allowed.has(type) || !surfaces.has(surface)) throw new Error('Unsupported UI event');
    // No free text, tokens, prompts or arbitrary payloads enter this log.
    const event = { id: root.crypto.randomUUID(), correlation_id: state.id, type,
      source: surface, timestamp: new Date().toISOString(), evidence_kind: 'ui_activity_only' };
    state.events = [...state.events, event].slice(-100);
    try { root.localStorage.setItem(key, JSON.stringify(state)); } catch (_) { storage = false; }
    for (const listener of listeners) {
      try { listener(snapshot()); } catch (error) { root.console.error('Buddy UI event consumer failed', error); }
    }
    return event;
  }
  root.addEventListener('storage', event => {
    if (event.key !== key) return;
    try {
      const next = JSON.parse(event.newValue);
      if (next && typeof next.id === 'string' && Array.isArray(next.events)) {
        state = next;
        for (const listener of listeners) {
          try { listener(snapshot()); } catch (error) { root.console.error('Buddy UI event consumer failed', error); }
        }
      }
    } catch (_) { /* Invalid browser state cannot become operational evidence. */ }
  });
  root.BuddySession = Object.freeze({ snapshot, emit, subscribe(listener) {
    listeners.add(listener); return () => listeners.delete(listener);
  } });
})(globalThis);

## Packages
(none needed)

## Notes
Uses existing shadcn/ui components already present in client/src/components/ui
Streaming: POST /api/conversations/:id/stream returns text/event-stream; client parses SSE lines starting with "data: " and validates against streams.chat.chunk
Dark mode: toggled by adding/removing `dark` class on documentElement; persisted in localStorage key "buddy.theme"

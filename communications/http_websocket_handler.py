# HTTP and WebSocket communication handler for Dreamcobots device communication.
# Provides a simple interface for sending/receiving data over HTTP and WebSocket.

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


class HTTPCommunicationHandler:
    """Lightweight HTTP server for device communication."""

    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self._server = None
        self._thread = None
        self.message_log = []
        self._handler_class = self._build_handler()

    def _build_handler(self):
        log = self.message_log

        class _RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                payload = json.dumps({"status": "ok", "path": self.path})
                self.wfile.write(payload.encode())
                log.append({"method": "GET", "path": self.path, "time": time.time()})

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode() if length else ""
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                payload = json.dumps({"status": "received", "body": body})
                self.wfile.write(payload.encode())
                log.append({"method": "POST", "path": self.path, "body": body, "time": time.time()})

            def log_message(self, fmt, *args):  # suppress default console output
                pass

        return _RequestHandler

    def start(self):
        """Start the HTTP server in a background thread."""
        self._server = HTTPServer((self.host, self.port), self._handler_class)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        print(f"[HTTP] Server started on {self.host}:{self.port}")

    def stop(self):
        """Stop the HTTP server."""
        if self._server:
            self._server.shutdown()
            self._server = None
        print("[HTTP] Server stopped.")

    def get_message_log(self):
        """Return a copy of all logged HTTP messages."""
        return list(self.message_log)


class WebSocketCommunicationHandler:
    """
    Manages WebSocket connections for real-time bi-directional communication.

    For full WebSocket support install the optional 'websockets' package:
        pip install websockets

    Without it, this class provides the interface and simulates messages in
    a lightweight in-memory message bus suitable for testing.
    """

    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.connected_clients = {}
        self.message_bus = []
        self._running = False

    def connect_client(self, client_id, metadata=None):
        """Register a client connection (used for simulation and testing)."""
        self.connected_clients[client_id] = {
            "metadata": metadata or {},
            "connected_at": time.time(),
        }
        print(f"[WebSocket] Client '{client_id}' connected.")
        return client_id

    def disconnect_client(self, client_id):
        """Remove a client connection."""
        if client_id in self.connected_clients:
            del self.connected_clients[client_id]
            print(f"[WebSocket] Client '{client_id}' disconnected.")

    def send(self, client_id, message):
        """Send a message to a specific connected client."""
        if client_id not in self.connected_clients:
            return {"error": f"Client '{client_id}' not connected"}
        entry = {
            "to": client_id,
            "message": message,
            "timestamp": time.time(),
        }
        self.message_bus.append(entry)
        print(f"[WebSocket] → {client_id}: {message}")
        return entry

    def broadcast(self, message):
        """Broadcast a message to all connected clients."""
        entries = []
        for client_id in list(self.connected_clients.keys()):
            entries.append(self.send(client_id, message))
        return entries

    def receive(self, client_id, message):
        """Simulate receiving a message from a client."""
        entry = {
            "from": client_id,
            "message": message,
            "timestamp": time.time(),
        }
        self.message_bus.append(entry)
        print(f"[WebSocket] ← {client_id}: {message}")
        return entry

    def get_message_bus(self):
        """Return all messages exchanged on this WebSocket handler."""
        return list(self.message_bus)

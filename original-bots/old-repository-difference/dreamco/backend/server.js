/**
 * DreamCo LeadGenBot — Backend Server
 *
 * Primary entry point for the HTTP server. Connects all API routes
 * and serves the frontend dashboard.
 *
 * Usage:
 *   node backend/server.js
 *   npm start
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');

const leadsRouter = require('./routes/leads');
const botsRouter = require('./routes/bots');
const { formatTimestamp } = require('./utils/helpers');

const app = express();
const PORT = process.env.PORT || 3000;

// ---------------------------------------------------------------------------
// Rate limiting — protect all routes from abuse
// ---------------------------------------------------------------------------
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 200, // max 200 requests per window per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests — please try again later.' },
});

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------
app.use(cors());
app.use(express.json());
app.use(limiter);

// Serve static frontend files from the /frontend directory
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// ---------------------------------------------------------------------------
// API Routes
// ---------------------------------------------------------------------------
app.use('/api/leads', leadsRouter);
app.use('/api/bots', botsRouter);

// Health check
app.get('/api/health', (_req, res) => {
  res.json({
    status: 'ok',
    service: 'DreamCo LeadGenBot API',
    version: '1.0.0',
    timestamp: formatTimestamp(),
    powered_by: 'DreamCo',
  });
});

// ---------------------------------------------------------------------------
// Catch-all: serve the frontend index for any unknown route
// ---------------------------------------------------------------------------
app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, '..', 'frontend', 'index.html'));
});

// ---------------------------------------------------------------------------
// Start server
// ---------------------------------------------------------------------------
app.listen(PORT, () => {
  console.log(`[DreamCo] LeadGenBot server running on http://localhost:${PORT}`);
  console.log(`[DreamCo] Dashboard: http://localhost:${PORT}/index.html`);
});

module.exports = app;

import express from 'express';

const app = express();
app.use(express.json());

const state = { startedAt: new Date().toISOString(), mode: process.env.MONEY_OS_MODE || 'dry-run' };

app.get('/health', (_req, res) => res.json({ ok: true, service: 'dreamco-money-os', ...state }));
app.get('/api/opportunities', (_req, res) => res.json({ opportunities: [], mode: state.mode, message: 'Connect authorized source adapters before live discovery.' }));
app.post('/api/run', (_req, res) => res.status(202).json({ accepted: true, mode: state.mode, next: 'run authorized source adapters, verify, score, then alert' }));

const port = Number(process.env.PORT || 3100);
app.listen(port, () => console.log(`DreamCo Money OS listening on ${port} (${state.mode})`));

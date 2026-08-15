import express from 'express';
import { scoreOpportunity, validateOpportunity, routeOpportunity } from './core.js';

const app = express();
app.use(express.json({limit:'1mb'}));

const registry = new Map();
const queue = [];

export function registerBot(name, handler) { registry.set(name, handler); }
export function enqueue(opportunity) { queue.push(opportunity); return queue.length; }

app.get('/health', (_req,res)=>res.json({ok:true, service:'dreamco-money-os', bots:registry.size, queued:queue.length}));
app.get('/bots', (_req,res)=>res.json({bots:[...registry.keys()]}));
app.post('/opportunities', (req,res)=>{
  const opportunity=req.body;
  const validation=validateOpportunity(opportunity);
  if(!validation.valid) return res.status(400).json(validation);
  const scored={...opportunity, route:routeOpportunity(opportunity), score:scoreOpportunity(opportunity)};
  enqueue(scored);
  res.status(201).json(scored);
});

export async function runQueue() {
  const results=[];
  while(queue.length) {
    const opportunity=queue.shift();
    const handler=registry.get(opportunity.route);
    results.push(handler ? await handler(opportunity) : {status:'queued', opportunity});
  }
  return results;
}

if (process.argv.includes('--once')) process.exitCode = 0;
else app.listen(process.env.PORT || 3000, ()=>console.log('DreamCo Money OS listening'));

export default app;

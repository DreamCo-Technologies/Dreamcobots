const tabs = ["Check", "Tokens", "RL", "Weights", "Patterns", "Bootcamp", "Gestures", "Rewards", "Connect", "Bank", "Qualify", "Gaps", "Scale", "SEO"];
let current = "Check";

const RL = [
  ["PPO", "Clip policy updates so a bad step cannot wreck the model."],
  ["TRPO", "Trust-region updates. Safer, slower than PPO."],
  ["A2C / A3C", "Actor-critic. Value guides the policy."],
  ["DQN", "Q-learning with a replay buffer and target network."],
  ["Double DQN", "Cuts the overestimate in DQN."],
  ["Dueling DQN", "Splits state value from action advantage."],
  ["SAC", "Soft actor-critic. Entropy keeps exploration alive."],
  ["TD3", "Twin critics. Good for continuous control."],
  ["DDPG", "Deterministic policy gradient for continuous actions."],
  ["REINFORCE", "Simple policy gradient. High variance."],
  ["GRPO", "Group relative policy optimization. Used in recent reasoning models."],
  ["DPO", "Direct preference optimization. No separate reward model."],
  ["IPO", "Identity preference optimization. A DPO variant."],
  ["KTO", "Kahneman-Tversky optimization. Works with unpaired feedback."],
  ["RLHF", "Reward model from human rankings, then policy update."],
  ["RLAIF", "AI feedback instead of human rankings."],
  ["Self-play", "Model plays against copies of itself."],
  ["Curriculum learning", "Easy tasks first, then harder ones."],
  ["Hindsight experience replay", "Failed goals still teach."],
  ["Curiosity / ICM", "Reward novelty so the agent explores."],
  ["Count-based exploration", "Rare states get a bonus."],
  ["UCB / Thompson", "Bandit methods for which experiment to run next."],
  ["Monte Carlo tree search", "Plan by simulating futures."],
  ["World models", "Learn a simulator, then plan inside it."],
  ["Offline RL", "Learn only from a fixed dataset."],
  ["Conservative Q-learning", "Stay close to the data in offline RL."],
  ["Decision transformer", "Treat RL as sequence prediction."],
  ["Recursive self-improvement", "Use better outputs to train the next round. Gate it."],
  ["Process reward models", "Score steps, not only the final answer."],
  ["Verifier-guided search", "Generate many answers, keep the ones a checker accepts."]
];

const WEIGHTS = [
  ["SGD", "Plain gradient step."],
  ["SGD + momentum", "Keeps velocity so flat spots move."],
  ["Nesterov", "Look-ahead momentum."],
  ["Adam", "Adaptive per-parameter rates."],
  ["AdamW", "Adam with decoupled weight decay. Default for most training."],
  ["Adafactor", "Adam with less memory."],
  ["Lion", "Sign-based update. Often cheaper."],
  ["Sophia", "Second-order hint. Can be faster on some runs."],
  ["RMSProp", "Older adaptive method."],
  ["Adagrad", "Good for sparse features, decays too hard."],
  ["LAMB", "Layer-wise adaptive rates for big batches."],
  ["LARS", "Layer-wise rate scaling."],
  ["Shampoo", "Preconditioner. Heavy, sometimes better."],
  ["Muon", "Orthogonalized momentum for hidden weights."],
  ["Schedule-free AdamW", "No hand-tuned decay schedule."],
  ["Warmup + cosine", "Standard schedule. Warm up, then decay."],
  ["Linear decay", "Simple and hard to break."],
  ["Constant LR", "Only for short probes."],
  ["Gradient clipping", "Cap the step so one batch cannot explode."],
  ["Weight decay", "Pulls weights toward zero. Regularizes."],
  ["Dropout", "Randomly drop units in training."],
  ["Label smoothing", "Stop the model from being 100% sure."],
  ["EMA weights", "Keep a smoothed copy for eval."],
  ["LoRA", "Train a small adapter, freeze the base."],
  ["QLoRA", "LoRA on a quantized base."],
  ["DoRA", "Magnitude plus direction adapters."],
  ["Full fine-tune", "Update every weight. Needs more data and care."],
  ["Prefix / prompt tuning", "Train only a short prefix."],
  ["Gradient checkpointing", "Trade compute for memory."],
  ["Mixed precision", "fp16 or bf16 updates with a stable master copy."]
];

const PATTERNS = [
  ["Singleton", "One shared instance. Use for a registry, not for hidden global state."],
  ["Builder", "Build a complex object step by step."],
  ["Factory method", "Let a subclass or function choose the concrete type."],
  ["Abstract factory", "Create a family of related objects."],
  ["Adapter", "Wrap a foreign API so your code can call it."],
  ["Facade", "One simple door in front of a messy subsystem."],
  ["Proxy", "Stand in for an object. Add access, cache, or remote calls."],
  ["Decorator", "Add behavior without changing the original."],
  ["Composite", "Treat a tree of objects like one object."],
  ["Strategy", "Swap algorithms at runtime."],
  ["Observer", "Notify listeners when state changes."],
  ["State", "Behavior changes with the current state."],
  ["Command", "Turn a request into an object you can queue or undo."],
  ["Template method", "Fixed steps, overridable parts."],
  ["Chain of responsibility", "Pass a request down a line until someone handles it."],
  ["Iterator", "Walk a collection without exposing how it is stored."],
  ["Mediator", "Objects talk through a hub, not to each other."],
  ["Memento", "Save and restore state."],
  ["Visitor", "Add operations without changing the objects."],
  ["Bridge", "Split abstraction from implementation."]
];

const HAND = [
  ["Open palm", "Stop or pause"],
  ["Closed fist", "Confirm"],
  ["Point", "Select"],
  ["Swipe left", "Back"],
  ["Swipe right", "Next"],
  ["Swipe up", "Open panel"],
  ["Swipe down", "Close panel"],
  ["Pinch", "Zoom or token detail"],
  ["Spread", "Expand"],
  ["Two-finger tap", "Secondary action"],
  ["Circle", "Refresh status"],
  ["Thumbs up", "Reward this output"],
  ["Thumbs down", "Penalize this output"],
  ["Peace", "Compare two attempts"],
  ["OK sign", "Accept score"],
  ["Wave", "Wake Buddy"],
  ["Hold two seconds", "Lock control"],
  ["Tap twice", "Repeat last command"],
  ["Draw L", "Open legal"],
  ["Draw C", "Open command center"],
  ["Draw T", "Open train hub"],
  ["Draw S", "System check"],
  ["Draw G", "Gap builder"],
  ["Draw R", "Rewards"],
  ["Draw V", "Verify output"],
  ["Draw B", "Bootcamp"],
  ["Draw M", "Memory settings"],
  ["Draw P", "Prompt builder"],
  ["Draw W", "Weight update"],
  ["Draw X", "Cancel"]
];

const VOICE = [
  ["Buddy check", "Run system check"],
  ["Buddy train", "Open train hub"],
  ["Buddy score", "Score the last output"],
  ["Buddy verify", "Run the checker"],
  ["Buddy reward", "Mark as reward"],
  ["Buddy skip", "Do not reward"],
  ["Buddy compare", "Compare N attempts"],
  ["Buddy temperature", "Show sampling controls"],
  ["Buddy tokens", "Count tokens in the box"],
  ["Buddy store on", "Allow chat storage"],
  ["Buddy store off", "Do not store this chat"],
  ["Buddy gap", "Open gap builder"],
  ["Buddy pattern", "Show design patterns"],
  ["Buddy algorithm", "Suggest a weight update"],
  ["Buddy experiment", "Pick the next useful test"],
  ["Buddy bootcamp", "Start pretrain lesson"],
  ["Buddy post", "Start post-train lesson"],
  ["Buddy connect", "Show API MCP RAG CLI A2A"],
  ["Buddy gesture", "List hand and voice gestures"],
  ["Buddy distill", "Open distillation prompt"],
  ["Buddy vocab", "Show vocab target"],
  ["Buddy punish", "Set penalty for bad practice"],
  ["Buddy partial", "Accept partial scores"],
  ["Buddy compete", "Run two systems against each other"],
  ["Buddy save", "Save this run"],
  ["Buddy export", "Export status"],
  ["Buddy ask", "Buddy asks the next useful question"],
  ["Buddy data", "Connect your own data"],
  ["Buddy stop", "Halt the current run"],
  ["Buddy status", "Live backend status"]
];

const TOKEN_EXAMPLES = [
  ["the", "1 token in most BPE models"],
  ["tokenization", "often 2-3 tokens"],
  ["DreamCo", "usually 2 tokens"],
  ["https://example.com", "several tokens because of punctuation"],
  ["1234567890", "digits often split"],
  ["a", "1 token, sometimes shared with a space"],
  [" ", "space is often glued to the next word"],
  ["Hello, world!", "comma and bang can be their own tokens"],
  ["def add(a, b):", "code splits on symbols"],
  ["return a + b", "operators often separate"],
  ["```python", "fence and language can split"],
  ["user: score this", "role tags add tokens"],
  ["<|end|>", "special tokens count as 1"],
  ["é", "accented letters may be multi-byte and multi-token"],
  ["👋", "emoji often 1-3 tokens"],
  ["JSON {\"a\":1}", "braces and quotes cost tokens"],
  ["repeat repeat repeat", "repeated words still cost each time"],
  ["aaaaaaaaaa", "long runs may stay one token or split"],
  ["New York City", "3 tokens is common"],
  ["machine learning", "2 tokens"],
  ["reinforcement learning", "2-3 tokens"],
  ["PPO", "1 token if in vocab, else spelled"],
  ["LoRA", "often 2 tokens"],
  ["byte", "1 token"],
  ["subword", "1-2 tokens"],
  ["150000", "usually more than one token"],
  ["system prompt of 200 words", "roughly 250-300 tokens"],
  ["one letter a", "1 token"],
  ["one byte 0x41", "shown as text, not raw byte"],
  ["shorter sequence wins", "cut filler before you cut facts"]
];

function setTab(name){ current = name; render(); }

function render(){
  document.getElementById("tabs").innerHTML = tabs.map(t => `<button class="tab ${t===current?"active":""}" onclick="setTab('${t}')">${t}</button>`).join("");
  const app = document.getElementById("app");
  if (current === "Check") {
    const mem = navigator.deviceMemory || "unknown";
    const cores = navigator.hardwareConcurrency || "unknown";
    const online = navigator.onLine ? "online" : "offline";
    app.innerHTML = `<div class="grid">
      <div class="card"><h2>System check</h2><p>Cores: ${cores}</p><p>Device memory hint: ${mem} GB</p><p>Network: ${online}</p><p class="ok">Ready for catalog, routing, and lessons.</p><p class="warn">This browser cannot train a 150k-vocab model. Use a GPU host for that.</p></div>
      <div class="card"><h2>Capability</h2><p>Build prompts: yes</p><p>Score outputs: yes</p><p>Run a full pretrain: no, needs a trainer host</p><p>Verify with a checker: yes</p></div>
      <div class="card"><h2>Live</h2><p><a href="command-center.html">Command Center</a></p><p><a href="backend-status.json">Backend status</a></p><p><a href="buddy.html">Buddy</a></p></div>
    </div>`;
  }
  if (current === "Tokens") {
    app.innerHTML = `<div class="card"><h2>Tokens per string</h2><textarea id="tok" rows="4" placeholder="Paste text"></textarea><button class="primary" onclick="countTok()">Count</button><p id="tokOut"></p><p>Rule of thumb: 1 token is about 4 characters in English. Code and JSON cost more. One letter is often one token. One raw byte is not automatically one token unless you train a byte-level model.</p></div>
    <div class="grid" style="margin-top:12px">${TOKEN_EXAMPLES.map(([a,b])=>`<div class="card"><strong>${a}</strong><p>${b}</p></div>`).join("")}</div>`;
  }
  if (current === "RL") {
    app.innerHTML = `<div class="grid">${RL.map(([n,d],i)=>`<div class="card"><strong>${i+1}. ${n}</strong><p>${d}</p></div>`).join("")}</div>`;
  }
  if (current === "Weights") {
    app.innerHTML = `<div class="grid">${WEIGHTS.map(([n,d],i)=>`<div class="card"><strong>${i+1}. ${n}</strong><p>${d}</p></div>`).join("")}</div>`;
  }
  if (current === "Patterns") {
    app.innerHTML = `<div class="grid">${PATTERNS.map(([n,d])=>`<div class="card"><strong>${n}</strong><p>${d}</p></div>`).join("")}</div>`;
  }
  if (current === "Bootcamp") {
    app.innerHTML = `<div class="grid">
      <div class="card"><h2>Pretrain series</h2><p>1. Data clean. 2. Tokenizer choice. 3. Short sequences first. 4. Loss and batch. 5. Eval set held out. 6. Checkpoint. 7. Do not claim a score you did not measure.</p></div>
      <div class="card"><h2>Post-train series</h2><p>1. Supervised examples. 2. Preference pairs. 3. Reward or DPO. 4. Verifier. 5. Temperature and top-p. 6. Regression tests. 7. Ship only what passed.</p></div>
      <div class="card"><h2>Vocab target</h2><p>150,000 is a target, not a result here. BPE and Unigram can reach it. Byte-level models use 256 byte tokens plus specials. Bigger vocab is not always better.</p></div>
      <div class="card"><h2>Jev</h2><p>Jev is a decision model. It returns a typed choice and a probability. It does not write sites. Use it to pick which region template to serve. Code still builds the page.</p></div>
    </div>`;
  }
  if (current === "Gestures") {
    app.innerHTML = `<h2>Hand</h2><div class="grid">${HAND.map(([n,d])=>`<div class="card"><strong>${n}</strong><p>${d}</p></div>`).join("")}</div><h2 style="margin-top:16px">Voice</h2><div class="grid">${VOICE.map(([n,d])=>`<div class="card"><strong>${n}</strong><p>${d}</p></div>`).join("")}</div>`;
  }
  if (current === "Rewards") {
    app.innerHTML = `<div class="card"><h2>What gets a reward</h2>
      <label><input type="checkbox" checked/> Correct final answer</label><br/>
      <label><input type="checkbox" checked/> Passed verifier</label><br/>
      <label><input type="checkbox"/> Partial score</label><br/>
      <label><input type="checkbox"/> Faster than baseline</label><br/>
      <label><input type="checkbox"/> Novel but valid</label>
      <p>Penalty for bad practice: <input id="pen" type="number" value="1" min="0" max="5"/> (0 none, 5 hard)</p>
      <p>Attempts to compare: <input id="n" type="number" value="4" min="1" max="32"/></p>
      <p>Temperature: <input id="temp" type="number" value="0.7" min="0" max="2" step="0.1"/></p>
      <button class="primary" onclick="saveReward()">Save policy</button>
      <p id="rewOut"></p>
    </div>`;
  }
  if (current === "Connect") {
    app.innerHTML = `<div class="grid">
      <div class="card"><h2>Ways in</h2><p>API, MCP, RAG, CLI, and A2A can all call Buddy if you expose the same route. Buddy can call them if you give a URL and a key. Keys stay needs-key until you add them.</p></div>
      <div class="card"><h2>Chat storage</h2><p><label><input type="checkbox" id="store" checked/> Store this chat</label></p><button class="primary" onclick="localStorage.setItem('buddyStore', document.getElementById('store').checked)">Save</button></div>
      <div class="card"><h2>Gap builder</h2><p>Gap engine is in the fleet repo. It scores missing, partial, and disconnected capabilities. This page links it. It does not invent a score.</p><p><a href="https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/dreamco_platform/software_gap_engine.py">Gap engine</a></p></div>
      <div class="card"><h2>Scale</h2><p>1 to 1000 users needs a host, auth, and a queue. This static page is the control surface. It is not the multi-tenant backend.</p></div>
    </div>`;
  }
  if (current === "Bank") {
    const bal = JSON.parse(localStorage.getItem("bank") || '{"store":0,"personal":0}');
    app.innerHTML = `<div class="grid">
      <div class="card"><h2>Store</h2><p>Demo balance: $${bal.store}</p><button class="primary" onclick="bankAdd('store',10)">Receive $10 demo</button></div>
      <div class="card"><h2>Personal</h2><p>Demo balance: $${bal.personal}</p><button class="primary" onclick="bankAdd('personal',10)">Receive $10 demo</button></div>
      <div class="card"><h2>Card connect</h2><p class="warn">Real card receive needs a licensed payment processor and a key. This page does not move real money.</p><input placeholder="Processor key (not stored on server)"/><button onclick="alert('Key stays in this browser. No charge is made.')">Save key locally</button></div>
    </div>`;
  }
  if (current === "Qualify") {
    const cores = navigator.hardwareConcurrency || 0;
    const mem = navigator.deviceMemory || 0;
    const gpu = (navigator.gpu ? "WebGPU present" : "No WebGPU");
    let verdict = "Catalog and lessons only.";
    if (cores >= 8 && mem >= 8) verdict = "Can fine-tune small adapters if you add a local trainer. Not a 150k pretrain.";
    if (cores >= 16 && mem >= 16) verdict = "Borderline for a small continued-pretrain. 150k vocab still needs a GPU host.";
    app.innerHTML = `<div class="card"><h2>This machine</h2><p>Cores: ${cores}</p><p>Memory hint: ${mem || "unknown"} GB</p><p>${gpu}</p><p class="ok">${verdict}</p><p>A 150,000-vocab train needs a GPU host, a tokenizer build, and a qualified trainer. This browser is the control panel.</p></div>`;
  }
  if (current === "Gaps") {
    app.innerHTML = `<div class="card"><h2>Gap registry</h2><p>Loading...</p></div>`;
    fetch("gaps.json").then(r=>r.json()).then(items=>{
      app.innerHTML = `<div class="grid">${items.map(i=>`<div class="card"><strong>${i.name}</strong><p class="${i.status==="live"?"ok":"warn"}">${i.status}</p><p>${i.note}</p></div>`).join("")}</div>`;
    }).catch(()=>{ app.innerHTML = `<p>gaps.json not loaded.</p>`; });
  }
  if (current === "Scale") {
    app.innerHTML = `<div class="card"><h2>Scale to 1000</h2><p>Control surface is here. To serve 1000 users you still need:</p><ul><li>A host (Pages is static)</li><li>Auth and roles</li><li>A queue for jobs</li><li>A database</li></ul><p>Buddy can generate the checklist. It cannot host the users from this page.</p></div>`;
  }
  if (current === "SEO") {
    const seo = [
      ["On-page", "Title, H1, meta description, internal links, alt text."],
      ["Technical", "Fast load, mobile, canonical, sitemap, robots, HTTPS."],
      ["Content", "One topic per page. Answer the query. Update stale pages."],
      ["Local", "City and region pages, consistent name/address, local links."],
      ["Off-page", "Mentions and links you earned. Do not buy links."],
      ["Schema", "FAQ, product, and article markup where it is true."],
      ["Search Console", "Index coverage, queries, and fixes."],
      ["Core Web Vitals", "LCP, INP, CLS. Measure before you claim a win."]
    ];
    app.innerHTML = `<div class="grid">${seo.map(([n,d])=>`<div class="card"><strong>${n}</strong><p>${d}</p></div>`).join("")}</div>`;
  }
}

function countTok(){
  const t = document.getElementById("tok").value || "";
  const approx = Math.max(1, Math.round(t.length / 4));
  document.getElementById("tokOut").textContent = `${t.length} characters, about ${approx} tokens, ${t.split(/\\s+/).filter(Boolean).length} words.`;
}
function saveReward(){
  const policy = { penalty: document.getElementById("pen").value, attempts: document.getElementById("n").value, temperature: document.getElementById("temp").value };
  localStorage.setItem("rewardPolicy", JSON.stringify(policy));
  document.getElementById("rewOut").textContent = "Saved in this browser.";
}
function bankAdd(which, amount){
  const bal = JSON.parse(localStorage.getItem("bank") || '{"store":0,"personal":0}');
  bal[which] = (bal[which] || 0) + amount;
  localStorage.setItem("bank", JSON.stringify(bal));
  render();
}
render();
